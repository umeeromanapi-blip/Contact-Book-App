# Software Requirements Specification (SRS)
## Contact Book App

- **Version:** 1.0
- **Status:** Initial Baseline
- **Project Type:** Beginner-Level Web Application
- **Backend:** Python Django
- **Frontend:** HTML, CSS
- **Database:** SQLite

---

## 1. Introduction

### 1.1 Purpose

Contact Book App aik simple web application hai jiska purpose users ko contacts ke naam aur phone numbers save karne aur unhein webpage par dekhne ki facility dena hai.

Is project ka primary learning objective frontend ko Django backend ke saath connect karna aur backend ke through SQLite database mein data store aur retrieve karna hai.

### 1.2 Project Scope

Application mein aik simple webpage hoga jahan user contact ka naam aur phone number enter kar sakega.

System submitted data ko Django backend ke through receive karega, SQLite database mein save karega aur saved contacts ko frontend par display karega.

Yeh project sirf basic contact management aur frontend-backend-database integration cover karega.

### 1.3 Intended Users

Is application ka aik general user hoga jo contact information enter aur view kar sakega.

Application beginner-level programming practice ke liye banayi jayegi.

## 2. Project Objectives

Project ke objectives yeh hain:

- HTML aur CSS se simple frontend form banana.
- Python Django se backend develop karna.
- SQLite database mein contacts store karna.
- Frontend form se data backend tak bhejna.
- Django backend se SQLite mein data save karna.
- Database se saved contacts retrieve karna.
- Retrieved contacts ko frontend par display karna.
- Form validation aur basic error handling implement karna.

## 3. Technology Stack

### 3.1 Frontend

- **HTML5:** Contact form aur contact list ka structure.
- **CSS3:** Page layout aur basic styling.
- **Django Templates:** Backend se milne wale contact records display karne ke liye.

### 3.2 Backend

- **Python:** Application ki programming language.
- **Django:** HTTP requests, application logic, URLs aur database operations handle karne ke liye.

### 3.3 Database

- **SQLite:** Contact records permanently store karne ke liye.
- **Django ORM:** Python models ke through database operations perform karne ke liye.

### 3.4 Development Tools

- Visual Studio Code
- Python
- Django
- Web browser

## 4. Functional Requirements

### FR-01: Display Contact Form

System aik webpage display karega jismein contact ka naam aur phone number enter karne ke liye do input fields aur aik **Save Contact** button hoga.

### FR-02: Receive Contact Information

System user ke submit kiye gaye naam aur phone number ko Django backend tak receive karega.

### FR-03: Validate Input

System check karega ke naam aur phone number empty na hon. Invalid input ki surat mein appropriate error message show kiya jayega.

### FR-04: Save Contact

Valid contact information Django backend ke through SQLite database mein save ki jayegi.

### FR-05: Display Confirmation

Contact successfully save hone par system user ko confirmation message display karega.

### FR-06: Retrieve Contacts

System SQLite database se previously saved contacts retrieve karega.

### FR-07: Display Contact List

System retrieved contacts ko webpage par naam aur phone number ke saath display karega.

### FR-08: Preserve Saved Data

Browser refresh ya Django server restart hone ke baad bhi saved contacts database mein available rahenge.

### FR-09: Handle Database Errors

Agar database operation fail ho, to system application crash hone ke bajaye appropriate error handling perform karega.

## 5. Non-Functional Requirements

### NFR-01: Usability

Interface simple aur beginner-friendly hona chahiye.

### NFR-02: Performance

Normal local development environment mein contact save aur list display operations reasonable response time mein complete hone chahiye.

### NFR-03: Data Persistence

Contacts SQLite database file mein persist hone chahiye.

### NFR-04: Security

Django POST forms mein CSRF protection enabled honi chahiye. User input ko Django ORM ke through handle kiya jayega.

### NFR-05: Maintainability

Frontend templates, backend views, URL configuration aur database models separate files mein organize hone chahiye.

### NFR-06: Compatibility

Application modern desktop web browsers mein locally run honi chahiye.

## 6. Database Requirements

### 6.1 Database Name

`db.sqlite3`

### 6.2 Table Name

`contacts_contact`

Django ORM model ke default naming convention ke mutabiq table create karega, jab tak custom table name configure na kiya jaye.

### 6.3 Contact Table Fields

| Field | Data Type | Requirement |
|---|---|---|
| `id` | Auto-generated integer | Primary key |
| `name` | Character field | Required |
| `phone` | Character field | Required |

Phone number ko character field mein store kiya jayega, kyun ke phone numbers mein leading zeros aur `+` sign ho sakta hai.

## 7. Application Workflow

1. User browser mein Contact Book webpage open karega.
2. System contact form display karega.
3. User naam aur phone number enter karega.
4. User **Save Contact** button click karega.
5. Browser POST request Django backend ko bhejega.
6. Django input validate karega.
7. Valid data SQLite database mein save hoga.
8. Django saved contacts retrieve karega.
9. Frontend template contacts ki list display karega.
10. User saved contact ko webpage par dekh sakega.

**Connection Flow:**

`Frontend Form → Django URL → Django View → Django Model/ORM → SQLite Database → Django Template → Browser`

## 8. Project File Structure

```text
ContactBook/
│
├── manage.py
├── db.sqlite3
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
└── contacts/
    ├── migrations/
    ├── templates/
    │   └── contacts/
    │       └── index.html
    ├── models.py
    ├── views.py
    ├── urls.py
    └── ...
```

CSS ko shuru mein HTML template ke andar ya baad mein separate static CSS file mein rakha ja sakta hai.

## 9. User Interface Requirements

Application ke main webpage par yeh elements honge:

- **Page heading:** Contact Book
- Name input field
- Phone Number input field
- Save Contact button
- Success ya validation message
- Saved Contacts heading
- Contacts ki list, jismein har contact ka naam aur phone number show ho

Design simple, clean aur responsive hona chahiye.

## 10. Out of Scope

Is version mein yeh features include nahi honge:

- User registration aur login
- Multiple users aur role-based permissions
- Contact edit aur delete
- Search aur filtering
- Email ya SMS notifications
- External APIs
- Cloud hosting
- REST API ya React integration
- Contact photos aur file uploads

Yeh features future versions mein add kiye ja sakte hain, lekin initial project ka scope nahi hain.

## 11. Testing Requirements

### TR-01: Empty Form Test

Empty name ya phone number submit karne par system validation message show kare.

### TR-02: Valid Contact Test

Valid naam aur phone number submit karne par contact database mein save ho.

### TR-03: Contact Display Test

Saved contact webpage ki list mein nazar aaye.

### TR-04: Persistence Test

Page refresh aur server restart ke baad saved contact available rahe.

### TR-05: Database Verification Test

Contact record SQLite database mein verify kiya ja sake.

### TR-06: CSRF Protection Test

POST form mein Django ki CSRF protection configured ho aur valid form submission successfully work kare.

## 12. Acceptance Criteria

Project tab complete samjha jayega jab:

- Contact form browser mein successfully open ho.
- Frontend se Django backend ko data send ho.
- Django backend contact data validate kare.
- Contact SQLite database mein save ho.
- Saved contacts webpage par display hon.
- Page refresh karne ke baad records available rahen.
- Basic validation aur error handling work kare.
- Application locally Django development server par run ho.

## 13. Final Deliverable

Final deliverable aik working Contact Book web application hogi jo HTML/CSS frontend, Django backend aur SQLite database ko integrate karegi.

Project ka central objective sirf webpage banana nahi, balkay frontend se backend aur backend se database tak complete data flow ko practically implement aur verify karna hai.
