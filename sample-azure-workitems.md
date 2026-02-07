# Sample Azure DevOps Work Items for Testing

This document provides ready-to-use examples of Epic, Feature, and User Stories to test the AI Test Case Generator.

---

## 📦 Epic: E-Commerce Platform Enhancement

**Work Item Type:** Epic  
**Title:** E-Commerce Platform Enhancement  
**Description:**  
As a business, we want to enhance our e-commerce platform to improve user experience, increase sales, and streamline checkout operations.

**Acceptance Criteria:**  
- Platform must support 10,000+ concurrent users
- Page load time under 2 seconds
- 99.9% uptime SLA

---

## ⚡ Feature: User Authentication & Profile Management

**Work Item Type:** Feature  
**Title:** User Authentication & Profile Management  
**Parent Epic:** E-Commerce Platform Enhancement  
**Description:**  
Implement secure user authentication and profile management system.

---

## 📝 User Story 1: User Registration with Email Validation

**Work Item Type:** User Story  
**Title:** User Registration with Email Validation  
**Parent Feature:** User Authentication & Profile Management  
**Description:**  
As a new customer, I want to register an account so that I can shop online.

**Acceptance Criteria (Gherkin Format):**

```
Scenario: User successfully registers with valid email
Given user is on registration page
When user enters valid email "newuser@example.com"
And user enters password "SecurePass123"
And user confirms password "SecurePass123"
And user clicks register button
Then user account is created
And confirmation email is sent
And user is redirected to login page

Scenario: User cannot register with invalid email format
Given user is on registration page
When user enters invalid email "invalid-email"
And user enters valid password "SecurePass123"
And user confirms password "SecurePass123"
And user clicks register button
Then error message "Please enter a valid email address" is displayed
And account is not created

Scenario: User cannot register with duplicate email
Given user is on registration page
When user enters email "existing@example.com"
And user enters password "SecurePass123"
And user confirms password "SecurePass123"
And user clicks register button
Then error message "Email already registered" is displayed
And account is not created

Scenario: User cannot register with short password
Given user is on registration page
When user enters valid email "newuser@example.com"
And user enters password "Ab1"
And user confirms password "Ab1"
And user clicks register button
Then error message "Password must be at least 8 characters" is displayed
And account is not created
```

---

## 📝 User Story 2: User Login and Session Management

**Work Item Type:** User Story  
**Title:** User Login and Session Management  
**Parent Feature:** User Authentication & Profile Management  
**Description:**  
As a registered user, I want to log in so that I can access my account.

**Acceptance Criteria (Gherkin Format):**

```
Scenario: User successfully logs in with valid credentials
Given user has valid account with email "user@example.com" and password "SecurePass123"
When user navigates to login page
And user enters email "user@example.com"
And user enters password "SecurePass123"
And user clicks Sign In button
Then user is redirected to dashboard
And welcome message "Welcome back, User!" is displayed

Scenario: User login fails with wrong password
Given user has valid account with email "user@example.com" and password "SecurePass123"
When user navigates to login page
And user enters email "user@example.com"
And user enters wrong password "WrongPass123"
And user clicks Sign In button
Then error message "Invalid email or password" is displayed
And user remains on login page

Scenario: User login fails with empty email
Given user is on login page
When user leaves email field empty
And user enters password "SecurePass123"
And user clicks Sign In button
Then error message "Email is required" is displayed below field

Scenario: User login fails with empty password
Given user is on login page
When user enters email "user@example.com"
And user leaves password field empty
And user clicks Sign In button
Then error message "Password is required" is displayed below field

Scenario: User is redirected to login after session timeout
Given user is logged in
When session expires after 30 minutes of inactivity
And user attempts to access dashboard
Then user is redirected to login page
And message "Your session has expired, please log in again" is displayed
```

---

## 📝 User Story 3: Product Search with Filters

**Work Item Type:** User Story  
**Title:** Product Search with Filters  
**Parent Feature:** User Authentication & Profile Management  
**Description:**  
As a shopper, I want to search for products so that I can find items I want to buy.

**Acceptance Criteria (Gherkin Format):**

```
Scenario: User can search for products by keyword
Given user is on homepage
When user enters "laptop" in search box
And user clicks search button
Then list of products containing "laptop" is displayed
And results are shown within 2 seconds

Scenario: User can filter search results by price range
Given search results for "laptop" are displayed
When user selects price filter "$500 - $1000"
Then only products between $500 and $1000 are shown
And filter icon indicates active filter

Scenario: User can filter search results by brand
Given search results for "phone" are displayed
When user selects brand filter "Samsung"
Then only Samsung products are shown

Scenario: Search with no results
Given user is on homepage
When user enters "xyz123nonexistent" in search box
And user clicks search button
Then message "No products found" is displayed
And suggestions "Try different keywords" are shown

Scenario: Search with special characters
Given user is on homepage
When user enters "laptop@#$%" in search box
And user clicks search button
Then error message "Special characters not allowed" is displayed
Or search ignores special characters and returns results

Scenario: Search with very long keyword
Given user is on homepage
When user enters 500-character search term
And user clicks search button
Then system handles input without error
And appropriate message is displayed
```

---

## 📝 User Story 4: Shopping Cart Operations

**Work Item Type:** User Story  
**Title:** Shopping Cart Operations  
**Parent Feature:** User Authentication & Profile Management  
**Description:**  
As a shopper, I want to manage my shopping cart so that I can review and modify items before checkout.

**Acceptance Criteria (Gherkin Format):**

```
Scenario: User can add product to cart
Given user is viewing product "iPhone 15"
When user clicks "Add to Cart" button
Then product is added to cart
And cart icon shows 1 item
And success message "Added to cart" is displayed

Scenario: User can add multiple products to cart
Given user is viewing product "Laptop"
And user has 1 item in cart
When user adds another product "Mouse"
Then cart shows 2 items
And total price is updated

Scenario: User can remove item from cart
Given user has 2 items in cart
When user clicks remove button on first item
Then item is removed from cart
And cart shows 1 item
And total price is updated

Scenario: User cannot add out-of-stock product
Given user is viewing out-of-stock product "Headphones"
When user clicks "Add to Cart" button
Then error message "Product out of stock" is displayed
And product is not added to cart

Scenario: Cart quantity update with invalid input
Given user has product in cart with quantity 5
When user enters "-1" in quantity field
Then system shows error "Invalid quantity"
And quantity remains at 5

Scenario: Cart persists after browser refresh
Given user has 3 items in cart
When user refreshes browser
Then cart still shows 3 items
And product details are preserved
```

---

## 📝 User Story 5: User Profile Management

**Work Item Type:** User Story  
**Title:** User Profile Management  
**Parent Feature:** User Authentication & Profile Management  
**Description:**  
As a registered user, I want to manage my profile so that I can update my personal information.

**Acceptance Criteria (Gherkin Format):**

```
Scenario: User can update profile name
Given user is logged in as "John Doe"
When user navigates to profile settings
And user changes name to "John Smith"
And user saves changes
Then profile shows name "John Smith"
And success message "Profile updated" is displayed

Scenario: User can update profile email
Given user is logged in with email "john@example.com"
When user navigates to profile settings
And user changes email to "johnsmith@example.com"
And user saves changes
Then profile shows email "johnsmith@example.com"
And verification email is sent

Scenario: User cannot update email to invalid format
Given user is on profile settings page
When user enters invalid email "invalid-email"
And user saves changes
Then error message "Please enter a valid email" is displayed
And email is not changed

Scenario: User can upload profile picture
Given user is on profile settings page
When user uploads image "photo.jpg"
And image is valid format (jpg, png)
Then profile picture is updated
And image displays correctly

Scenario: User cannot upload invalid file type
Given user is on profile settings page
When user uploads file "document.pdf"
Then error message "Invalid file type. Only jpg, png allowed" is displayed
And file is not uploaded

Scenario: Profile phone number validation
Given user is on profile settings page
When user enters phone number "12345"
Then error message "Invalid phone number" is displayed
And phone is not saved

Scenario: User can delete account
Given user is on account settings page
When user clicks "Delete Account"
And user confirms deletion with password
Then account is permanently deleted
And user is logged out
```

---

## 📝 User Story 6: Password Reset Functionality

**Work Item Type:** User Story  
**Title:** Password Reset Functionality  
**Parent Feature:** User Authentication & Profile Management  
**Description:**  
As a user who forgot my password, I want to reset my password so that I can regain access to my account.

**Acceptance Criteria (Gherkin Format):**

```
Scenario: User requests password reset with valid email
Given user is on login page
When user clicks "Forgot Password"
And user enters email "registered@example.com"
And user submits request
Then password reset email is sent
And message "Check your email for reset instructions" is displayed

Scenario: User cannot request reset with unregistered email
Given user is on forgot password page
When user enters email "notregistered@example.com"
And user submits request
Then error message "Email not found" is displayed

Scenario: User can set new password with valid reset link
Given user received password reset email
When user clicks reset link
And user enters new password "NewSecurePass123"
And user confirms password "NewSecurePass123"
And user submits
Then password is updated
And user can login with new password

Scenario: Password reset fails with weak password
Given user is on password reset page with valid token
When user enters password "123"
And user confirms password "123"
And user submits
Then error message "Password must be at least 8 characters" is displayed

Scenario: Password reset link expires after 1 hour
Given password reset link was generated 2 hours ago
When user tries to use link
Then error message "Reset link has expired" is displayed
And user must request new link

Scenario: Password reset prevents using same password
Given user reset password to "NewPass123"
When user requests reset again
And sets password to "NewPass123"
Then error message "Cannot use previous password" is displayed
```

---

## 🎯 Quick Import Instructions

1. **Create Epic first** in Azure Boards
2. **Create Feature** and link it to the Epic
3. **Create User Stories** and link each to the Feature
4. **Ensure each User Story has:**
   - Clear title
   - Description
   - **Acceptance Criteria** (the AI uses this!)
5. **Run the pipeline** - it will:
   - Fetch new User Stories
   - Generate test cases for each
   - Create Test Plan (from Epic)
   - Create Test Suite (from Feature)
   - Create Test Cases (from User Stories)
   - Link everything together

---

## 📊 Expected Test Case Generation

For **User Story 1 (Registration)** with the enhanced prompt, expect ~15-20 test cases covering:

| Category | Expected Count | Examples |
|----------|----------------|----------|
| Positive | 3-4 | Valid registration, email confirmation |
| Negative | 5-7 | Invalid email, duplicate email, short password |
| Edge | 6-9 | Empty fields, max length, SQL injection, XSS, special chars |
| Security | 2-3 | SQL injection, XSS, brute force prevention |

**Total: ~15-20 comprehensive test cases per User Story**
