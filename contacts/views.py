from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
import csv
import io
import json
import logging
from .models import Contact, ActivityLog, log_activity
from .forms import ContactForm, CSVImportForm, UserRegistrationForm, UserLoginForm

logger = logging.getLogger(__name__)


def contact_list(request):
    """
    Primary view for Epic 1, 2, 3 & 4: Contact Book Application.
    Supports:
    - Multi-user isolation (authenticated users manage their contacts, guests view demo space)
    - Multi-field search, tab filtering, category filtering, sorting, pagination
    - Activity logging
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact = form.save(commit=False)
                if request.user.is_authenticated:
                    contact.user = request.user
                contact.save()
                log_activity(request.user, 'create', f"Added \"{contact.name}\" ({contact.phone})")
                messages.success(request, f"✨ Contact \"{contact.name}\" saved successfully!")
                return redirect('contact_list')
            except DatabaseError as e:
                logger.exception("Database error occurred while saving contact: %s", e)
                messages.error(request, "A database error occurred while saving the contact. Please try again.")
        else:
            messages.error(request, "Unable to save contact. Please review the highlighted fields below.")
    else:
        form = ContactForm()

    # Query parameters
    search_query = request.GET.get('q', '').strip()
    active_tab = request.GET.get('tab', 'all').strip().lower()
    selected_category = request.GET.get('category', '').strip().lower()
    sort_order = request.GET.get('sort', 'newest').strip().lower()
    page_number = request.GET.get('page', 1)

    try:
        # Multi-user isolation: if logged in, filter to user's contacts (plus unassigned legacy demo contacts)
        if request.user.is_authenticated:
            queryset = Contact.objects.filter(Q(user=request.user) | Q(user__isnull=True))
        else:
            queryset = Contact.objects.all()

        # Tab filtering
        if active_tab == 'favorites':
            queryset = queryset.filter(is_favorite=True)

        # Category filtering
        if selected_category and selected_category != 'all':
            queryset = queryset.filter(category=selected_category)

        # Search filtering
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(notes__icontains=search_query)
            )

        # Sorting
        if sort_order == 'oldest':
            queryset = queryset.order_by('id')
        elif sort_order == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort_order == 'name_desc':
            queryset = queryset.order_by('-name')
        else:
            queryset = queryset.order_by('-id')

        # Pagination: 8 contacts per page
        paginator = Paginator(queryset, 8)
        try:
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        total_contacts = queryset.count()
        favorite_count = queryset.filter(is_favorite=True).count()
        category_counts = dict(
            queryset.values('category')
            .annotate(count=Count('id'))
            .values_list('category', 'count')
        )
    except DatabaseError as e:
        logger.exception("Database error occurred while retrieving contacts: %s", e)
        page_obj = []
        paginator = None
        total_contacts = 0
        favorite_count = 0
        category_counts = {}
        messages.error(request, "Could not load contacts from the database.")

    context = {
        'form': form,
        'csv_import_form': CSVImportForm(),
        'contacts': page_obj,
        'page_obj': page_obj,
        'total_contacts': total_contacts,
        'favorite_count': favorite_count,
        'category_counts': category_counts,
        'categories': Contact.CATEGORY_CHOICES,
        'search_query': search_query,
        'active_tab': active_tab,
        'selected_category': selected_category,
        'sort_order': sort_order,
    }
    return render(request, 'contacts/index.html', context)


def contact_update(request, pk):
    """
    Update an existing contact with audit logging.
    """
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            try:
                updated_contact = form.save()
                log_activity(request.user, 'update', f"Updated \"{updated_contact.name}\"")
                messages.success(request, f"✨ Contact \"{contact.name}\" updated successfully!")
                return redirect('contact_list')
            except DatabaseError as e:
                logger.exception("Database error occurred while updating contact: %s", e)
                messages.error(request, "A database error occurred while updating the contact.")
        else:
            messages.error(request, "Please correct the errors in the update form.")
    else:
        form = ContactForm(instance=contact)

    context = {
        'form': form,
        'contact': contact,
    }
    return render(request, 'contacts/edit.html', context)


def contact_delete(request, pk):
    """
    Delete an existing contact with audit logging.
    """
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        contact_name = contact.name
        try:
            contact.delete()
            log_activity(request.user, 'delete', f"Deleted \"{contact_name}\"")
            messages.success(request, f"🗑️ Contact \"{contact_name}\" was deleted.")
        except DatabaseError as e:
            logger.exception("Database error occurred while deleting contact: %s", e)
            messages.error(request, "A database error occurred while deleting the contact.")
        return redirect('contact_list')

    return render(request, 'contacts/confirm_delete.html', {'contact': contact})


def contact_toggle_favorite(request, pk):
    """
    Toggle the favorite/star status of a contact with audit logging.
    """
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        try:
            contact.is_favorite = not contact.is_favorite
            contact.save(update_fields=['is_favorite'])
            status = "starred" if contact.is_favorite else "unstarred"
            log_activity(request.user, 'favorite', f"{status.capitalize()} \"{contact.name}\"")
            messages.success(request, f"⭐ \"{contact.name}\" {status}.")
        except DatabaseError as e:
            logger.exception("Database error toggling favorite: %s", e)
            messages.error(request, "Could not update favorite status.")
    return redirect('contact_list')


def contact_export_csv(request):
    """
    Export contacts to CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contact_book_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Phone', 'Email', 'Category', 'Notes', 'Favorite', 'Created At'])

    if request.user.is_authenticated:
        contacts = Contact.objects.filter(Q(user=request.user) | Q(user__isnull=True)).order_by('id')
    else:
        contacts = Contact.objects.all().order_by('id')

    for c in contacts:
        writer.writerow([
            c.id,
            c.name,
            c.phone,
            c.email or '',
            c.category,
            c.notes or '',
            'Yes' if c.is_favorite else 'No',
            c.created_at.strftime('%Y-%m-%d %H:%M:%S') if c.created_at else ''
        ])

    log_activity(request.user, 'bulk', "Exported contacts directory as CSV")
    return response


def contact_export_vcard(request, pk):
    """
    Epic 4: Generates and downloads a standard vCard (.vcf) file for a contact.
    Directly importable on iOS, Android, and Outlook.
    """
    contact = get_object_or_404(Contact, pk=pk)
    vcard_lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{contact.name}",
        f"TEL;TYPE=CELL:{contact.phone}",
    ]
    if contact.email:
        vcard_lines.append(f"EMAIL;TYPE=INTERNET:{contact.email}")
    if contact.category:
        vcard_lines.append(f"CATEGORIES:{contact.get_category_display()}")
    if contact.notes:
        vcard_lines.append(f"NOTE:{contact.notes}")
    vcard_lines.append("END:VCARD")
    vcard_content = "\r\n".join(vcard_lines) + "\r\n"

    response = HttpResponse(vcard_content, content_type="text/vcard; charset=utf-8")
    safe_name = "".join(c for c in contact.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"{safe_name or 'contact'}.vcf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    log_activity(request.user, 'bulk', f"Exported vCard for \"{contact.name}\"")
    return response


def contact_download_sample_csv(request):
    """
    Downloads a template CSV file for bulk import.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_contacts_import.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Category', 'Notes', 'Favorite'])
    writer.writerow(['Sarah Connor', '+1 555-0144', 'sarah@resistance.org', 'work', 'Cyberdyne liaison', 'Yes'])
    writer.writerow(['Miles Dyson', '+1 555-0199', 'miles@cyberdyne.com', 'vip', 'Lead systems architect', 'No'])
    writer.writerow(['John Connor', '0300-9876543', 'john@future.net', 'family', 'Primary emergency contact', 'Yes'])
    return response


def contact_import_csv(request):
    """
    Handles bulk CSV file upload with user ownership and activity logging.
    """
    if request.method != 'POST':
        return redirect('contact_list')

    form = CSVImportForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Invalid file uploaded. Please upload a valid .csv file under 2MB.")
        return redirect('contact_list')

    csv_file = request.FILES['csv_file']
    try:
        decoded_file = csv_file.read().decode('utf-8-sig', errors='ignore')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)

        header = next(reader, None)
        if not header:
            messages.error(request, "Uploaded CSV file is empty.")
            return redirect('contact_list')

        header_lower = [h.strip().lower() for h in header]
        name_idx = next((i for i, h in enumerate(header_lower) if 'name' in h), 0)
        phone_idx = next((i for i, h in enumerate(header_lower) if 'phone' in h), 1)
        email_idx = next((i for i, h in enumerate(header_lower) if 'email' in h), -1)
        cat_idx = next((i for i, h in enumerate(header_lower) if 'cat' in h), -1)
        notes_idx = next((i for i, h in enumerate(header_lower) if 'note' in h), -1)
        fav_idx = next((i for i, h in enumerate(header_lower) if 'fav' in h or 'star' in h), -1)

        valid_categories = dict(Contact.CATEGORY_CHOICES).keys()
        created_count = 0
        skipped_count = 0

        for row in reader:
            if not row or len(row) <= max(name_idx, phone_idx):
                skipped_count += 1
                continue

            name = row[name_idx].strip()
            phone = row[phone_idx].strip()

            if not name or not phone:
                skipped_count += 1
                continue

            email = row[email_idx].strip() if email_idx != -1 and len(row) > email_idx else ''
            cat_val = row[cat_idx].strip().lower() if cat_idx != -1 and len(row) > cat_idx else 'personal'
            if cat_val not in valid_categories:
                cat_val = 'personal'

            notes = row[notes_idx].strip() if notes_idx != -1 and len(row) > notes_idx else ''
            fav_raw = row[fav_idx].strip().lower() if fav_idx != -1 and len(row) > fav_idx else ''
            is_fav = fav_raw in ['yes', 'true', '1', 'y']

            Contact.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name[:100],
                phone=phone[:20],
                email=email[:100],
                category=cat_val,
                notes=notes,
                is_favorite=is_fav
            )
            created_count += 1

        log_activity(request.user, 'import', f"Imported {created_count} contacts from CSV")
        messages.success(request, f"🎉 Import Complete: Successfully imported {created_count} contacts! ({skipped_count} skipped)")
    except Exception as e:
        logger.exception("Error processing CSV import: %s", e)
        messages.error(request, f"Error processing CSV file: {str(e)}")

    return redirect('contact_list')


def contact_bulk_action(request):
    """
    Bulk actions on multiple contacts.
    """
    if request.method != 'POST':
        return redirect('contact_list')

    action = request.POST.get('bulk_action')
    contact_ids = request.POST.getlist('selected_contacts')

    if not contact_ids:
        messages.error(request, "No contacts were selected for bulk action.")
        return redirect('contact_list')

    queryset = Contact.objects.filter(id__in=contact_ids)
    count = queryset.count()

    if action == 'delete':
        queryset.delete()
        log_activity(request.user, 'bulk', f"Bulk deleted {count} contacts")
        messages.success(request, f"🗑️ Successfully deleted {count} contacts.")
    elif action == 'favorite':
        queryset.update(is_favorite=True)
        log_activity(request.user, 'bulk', f"Bulk starred {count} contacts")
        messages.success(request, f"⭐ Marked {count} contacts as favorites.")
    elif action == 'unfavorite':
        queryset.update(is_favorite=False)
        log_activity(request.user, 'bulk', f"Bulk unstarred {count} contacts")
        messages.success(request, f"☆ Removed {count} contacts from favorites.")
    elif action.startswith('category:'):
        new_cat = action.split(':', 1)[1]
        if new_cat in dict(Contact.CATEGORY_CHOICES):
            queryset.update(category=new_cat)
            log_activity(request.user, 'bulk', f"Changed category to {new_cat} for {count} contacts")
            messages.success(request, f"🏷️ Updated category to {new_cat.capitalize()} for {count} contacts.")
    else:
        messages.error(request, "Unknown bulk action specified.")

    return redirect('contact_list')


# =============================================================================
# EPIC 4: USER AUTHENTICATION & MULTI-USER ISOLATION
# =============================================================================

def user_register(request):
    """
    Epic 4: Register new user account.
    """
    if request.user.is_authenticated:
        return redirect('contact_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data.get('email', ''),
                password=form.cleaned_data['password']
            )
            login(request, user)
            log_activity(user, 'create', f"New user account registered ({user.username})")
            messages.success(request, f"🎉 Welcome {user.username}! Your private contact book is ready.")
            return redirect('contact_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'contacts/register.html', {'form': form})


def user_login(request):
    """
    Epic 4: Login existing user.
    """
    if request.user.is_authenticated:
        return redirect('contact_list')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"👋 Welcome back, {user.username}!")
                return redirect('contact_list')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'contacts/login.html', {'form': form})


def user_demo_login(request):
    """
    Epic 4: Instant 1-Click Demo Login.
    Creates or retrieves 'demo_user' and authenticates instantly.
    """
    demo_user, created = User.objects.get_or_create(username='demo_user', defaults={'email': 'demo@contactbook.com'})
    if created:
        demo_user.set_password('DemoUser2026!')
        demo_user.save()

    login(request, demo_user)
    messages.success(request, "🚀 Logged in as Demo User! You now have access to authenticated private features.")
    return redirect('contact_list')


def user_logout(request):
    """
    Epic 4: Log out user.
    """
    username = request.user.username if request.user.is_authenticated else 'User'
    logout(request)
    messages.success(request, f"Logged out successfully. Have a great day, {username}!")
    return redirect('contact_list')


# =============================================================================
# EPIC 4: VISUAL ANALYTICS DASHBOARD
# =============================================================================

def analytics_dashboard(request):
    """
    Epic 4: Visual Analytics & Insights Hub.
    Calculates contact metrics, category distributions, star ratios, and audit logs.
    """
    if request.user.is_authenticated:
        queryset = Contact.objects.filter(Q(user=request.user) | Q(user__isnull=True))
        logs_queryset = ActivityLog.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    else:
        queryset = Contact.objects.all()
        logs_queryset = ActivityLog.objects.all()

    total = queryset.count()
    favorites = queryset.filter(is_favorite=True).count()
    fav_pct = round((favorites / total * 100), 1) if total > 0 else 0

    with_email = queryset.exclude(email='').count()
    email_pct = round((with_email / total * 100), 1) if total > 0 else 0

    with_notes = queryset.exclude(notes='').count()
    notes_pct = round((with_notes / total * 100), 1) if total > 0 else 0

    # Category Breakdown
    cat_counts = dict(
        queryset.values('category')
        .annotate(count=Count('id'))
        .values_list('category', 'count')
    )

    category_stats = []
    for key, label in Contact.CATEGORY_CHOICES:
        count = cat_counts.get(key, 0)
        pct = round((count / total * 100), 1) if total > 0 else 0
        category_stats.append({
            'key': key,
            'label': label,
            'count': count,
            'pct': pct
        })

    recent_activities = logs_queryset[:10]
    recent_contacts = queryset.order_by('-id')[:5]

    context = {
        'total_contacts': total,
        'favorite_contacts': favorites,
        'fav_pct': fav_pct,
        'with_email': with_email,
        'email_pct': email_pct,
        'with_notes': with_notes,
        'notes_pct': notes_pct,
        'category_stats': category_stats,
        'recent_activities': recent_activities,
        'recent_contacts': recent_contacts,
    }
    return render(request, 'contacts/dashboard.html', context)


# =============================================================================
# REST API ENDPOINTS (JSON)
# =============================================================================

@csrf_exempt
def api_contact_list_create(request):
    """
    REST API: GET /api/contacts/ & POST /api/contacts/
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', '').strip().lower()
        favorites_only = request.GET.get('favorites', '').strip().lower() in ['1', 'true', 'yes']

        queryset = Contact.objects.all()
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        if category:
            queryset = queryset.filter(category=category)
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query) |
                Q(notes__icontains=query)
            )

        data = [c.to_dict() for c in queryset]
        return JsonResponse({
            'success': True,
            'count': len(data),
            'contacts': data
        })

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)

        name = body.get('name', '').strip()
        phone = body.get('phone', '').strip()
        email = body.get('email', '').strip()
        category = body.get('category', 'personal').strip().lower()
        notes = body.get('notes', '').strip()
        is_favorite = bool(body.get('is_favorite', False))

        if not name or not phone:
            return JsonResponse({'success': False, 'error': 'Name and phone are required fields'}, status=400)

        valid_categories = dict(Contact.CATEGORY_CHOICES).keys()
        if category not in valid_categories:
            category = 'personal'

        contact = Contact.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name[:100],
            phone=phone[:20],
            email=email[:100],
            category=category,
            notes=notes,
            is_favorite=is_favorite
        )
        log_activity(request.user, 'create', f"REST API created \"{contact.name}\"")
        return JsonResponse({
            'success': True,
            'message': 'Contact created successfully',
            'contact': contact.to_dict()
        }, status=201)

    return JsonResponse({'success': False, 'error': f'Method {request.method} not allowed'}, status=405)


@csrf_exempt
def api_contact_detail(request, pk):
    """
    REST API: GET /api/contacts/<id>/, PUT/PATCH /api/contacts/<id>/, DELETE /api/contacts/<id>/
    """
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'Contact with ID {pk} not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'success': True, 'contact': contact.to_dict()})

    elif request.method in ['PUT', 'PATCH']:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)

        if 'name' in body:
            name = body['name'].strip()
            if not name:
                return JsonResponse({'success': False, 'error': 'Name cannot be blank'}, status=400)
            contact.name = name[:100]

        if 'phone' in body:
            phone = body['phone'].strip()
            if not phone:
                return JsonResponse({'success': False, 'error': 'Phone cannot be blank'}, status=400)
            contact.phone = phone[:20]

        if 'email' in body:
            contact.email = body['email'].strip()[:100]

        if 'category' in body:
            cat = body['category'].strip().lower()
            if cat in dict(Contact.CATEGORY_CHOICES):
                contact.category = cat

        if 'notes' in body:
            contact.notes = body['notes'].strip()

        if 'is_favorite' in body:
            contact.is_favorite = bool(body['is_favorite'])

        contact.save()
        log_activity(request.user, 'update', f"REST API updated \"{contact.name}\"")
        return JsonResponse({
            'success': True,
            'message': 'Contact updated successfully',
            'contact': contact.to_dict()
        })

    elif request.method == 'DELETE':
        name = contact.name
        contact.delete()
        log_activity(request.user, 'delete', f"REST API deleted \"{name}\"")
        return JsonResponse({
            'success': True,
            'message': f'Contact #{pk} successfully deleted'
        })

    return JsonResponse({'success': False, 'error': f'Method {request.method} not allowed'}, status=405)


def api_contact_stats(request):
    """
    REST API: GET /api/contacts/stats/
    """
    total = Contact.objects.count()
    favorites = Contact.objects.filter(is_favorite=True).count()
    by_category = dict(
        Contact.objects.values('category')
        .annotate(count=Count('id'))
        .values_list('category', 'count')
    )

    return JsonResponse({
        'success': True,
        'stats': {
            'total_contacts': total,
            'favorite_contacts': favorites,
            'category_breakdown': by_category
        }
    })
