"""
CLI Menu Interface for the Library Management System - Milestone 2.
Provides an interactive command-line menu for all system operations.
"""

from datetime import date, timedelta
import book_search
import borrowers
import loans
import fines
from init_db import init_db


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("Library Management System - Milestone 2")
    print("=" * 60)


def print_menu():
    """Print the main menu options."""
    print("\nMain Menu:")
    print("1. Search books")
    print("2. Checkout book")
    print("3. Check-in book")
    print("4. Add borrower")
    print("5. Update fines")
    print("6. View fines")
    print("7. Exit")
    print("-" * 60)


def search_books_menu():
    """Menu option 1: Search for books."""
    print("\n--- Search Books ---")
    query = input("Enter search query (ISBN, title, or author): ").strip()
    
    if not query:
        print("Error: Search query cannot be empty.")
        return
    
    try:
        results = book_search.search_books(query)
        
        if not results:
            print(f"\nNo books found matching '{query}'")
            return
        
        print(f"\nFound {len(results)} book(s):")
        print("-" * 80)
        print(f"{'#':<4} {'ISBN':<15} {'Title':<35} {'Authors':<20} {'Status':<6}")
        print("-" * 80)
        
        for idx, book in enumerate(results, 1):
            # Truncate long titles/authors for display
            title = book['title'][:33] + "..." if len(book['title']) > 35 else book['title']
            authors = book['authors'][:18] + "..." if len(book['authors']) > 20 else book['authors']
            if not authors:
                authors = "N/A"
            
            print(f"{idx:<4} {book['isbn']:<15} {title:<35} {authors:<20} {book['status']:<6}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"Error searching books: {e}")


def checkout_book_menu():
    """Menu option 2: Checkout a book."""
    print("\n--- Checkout Book ---")
    
    try:
        isbn = input("Enter ISBN: ").strip()
        if not isbn:
            print("Error: ISBN cannot be empty.")
            return
        
        card_id = input("Enter Borrower Card ID: ").strip()
        if not card_id:
            print("Error: Card ID cannot be empty.")
            return
        
        # Verify borrower exists
        borrower = borrowers.get_borrower_by_card(card_id)
        if not borrower:
            print(f"Error: Borrower with Card ID {card_id} not found.")
            return
        
        print(f"\nBorrower: {borrower['Bname']}")
        print(f"Checking out book ISBN: {isbn}...")
        
        loan_id = loans.checkout_book(isbn, card_id)
        print(f"\n✓ Successfully checked out book!")
        print(f"  Loan ID: {loan_id}")
        print(f"  Due Date: {date.today() + timedelta(days=14)}")
        
    except loans.MaxLoansError as e:
        print(f"\n✗ Checkout failed: {e}")
    except loans.BookNotAvailableError as e:
        print(f"\n✗ Checkout failed: {e}")
    except loans.UnpaidFinesError as e:
        print(f"\n✗ Checkout failed: {e}")
    except Exception as e:
        print(f"\n✗ Error during checkout: {e}")


def checkin_book_menu():
    """Menu option 3: Check-in books."""
    print("\n--- Check-in Books ---")
    
    try:
        # First, search for active loans
        print("\nSearch for loans to check in:")
        print("1. By ISBN")
        print("2. By Borrower Card ID")
        print("3. By Borrower Name")
        print("4. Show all active loans")
        
        search_choice = input("\nEnter search option (1-4): ").strip()
        
        active_loans = []
        
        if search_choice == "1":
            isbn = input("Enter ISBN: ").strip()
            if isbn:
                active_loans = loans.find_active_loans(isbn=isbn)
        elif search_choice == "2":
            card_id = input("Enter Borrower Card ID: ").strip()
            if card_id:
                active_loans = loans.find_active_loans(card_id=card_id)
        elif search_choice == "3":
            name_query = input("Enter borrower name (substring): ").strip()
            if name_query:
                active_loans = loans.find_active_loans(name_query=name_query)
        elif search_choice == "4":
            active_loans = loans.find_active_loans()
        else:
            print("Invalid option.")
            return
        
        if not active_loans:
            print("\nNo active loans found matching your criteria.")
            return
        
        # Display active loans
        print(f"\nFound {len(active_loans)} active loan(s):")
        print("-" * 90)
        print(f"{'#':<4} {'Loan ID':<10} {'ISBN':<15} {'Title':<30} {'Borrower':<20} {'Due Date':<12}")
        print("-" * 90)
        
        for idx, loan in enumerate(active_loans, 1):
            title = loan['title'][:28] + "..." if len(loan['title']) > 30 else loan['title']
            borrower = loan['borrower_name'][:18] + "..." if len(loan['borrower_name']) > 20 else loan['borrower_name']
            due_date_str = loan['due_date'].strftime('%Y-%m-%d') if isinstance(loan['due_date'], date) else str(loan['due_date'])
            
            print(f"{idx:<4} {loan['loan_id']:<10} {loan['isbn']:<15} {title:<30} {borrower:<20} {due_date_str:<12}")
        
        print("-" * 90)
        
        # Select loans to check in
        loan_ids_input = input("\nEnter loan ID(s) to check in (comma-separated, e.g., 1,2,3): ").strip()
        if not loan_ids_input:
            print("No loans selected.")
            return
        
        try:
            loan_ids = [int(x.strip()) for x in loan_ids_input.split(',')]
            
            # Verify loan IDs exist in the results
            valid_loan_ids = [loan['loan_id'] for loan in active_loans]
            invalid_ids = [lid for lid in loan_ids if lid not in valid_loan_ids]
            
            if invalid_ids:
                print(f"Warning: Loan ID(s) {invalid_ids} not found in active loans. Proceeding with valid IDs.")
                loan_ids = [lid for lid in loan_ids if lid in valid_loan_ids]
            
            if not loan_ids:
                print("No valid loan IDs to check in.")
                return
            
            # Confirm
            print(f"\nChecking in {len(loan_ids)} loan(s): {loan_ids}")
            confirm = input("Confirm? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("Check-in cancelled.")
                return
            
            loans.checkin_loans(loan_ids)
            print(f"\n✓ Successfully checked in {len(loan_ids)} loan(s)!")
            
        except ValueError:
            print("Error: Invalid loan ID format. Please enter numbers separated by commas.")
        except Exception as e:
            print(f"\n✗ Error during check-in: {e}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


def add_borrower_menu():
    """Menu option 4: Add a new borrower."""
    print("\n--- Add Borrower ---")
    
    try:
        ssn = input("Enter SSN: ").strip()
        if not ssn:
            print("Error: SSN cannot be empty.")
            return
        
        name = input("Enter full name: ").strip()
        if not name:
            print("Error: Name cannot be empty.")
            return
        
        address = input("Enter address: ").strip()
        if not address:
            print("Error: Address cannot be empty.")
            return
        
        phone = input("Enter phone number: ").strip()
        if not phone:
            print("Error: Phone number cannot be empty.")
            return
        
        print(f"\nCreating borrower...")
        print(f"  Name: {name}")
        print(f"  SSN: {ssn}")
        print(f"  Address: {address}")
        print(f"  Phone: {phone}")
        
        card_id = borrowers.create_borrower(ssn, name, address, phone)
        print(f"\n✓ Successfully created borrower!")
        print(f"  Card ID: {card_id}")
        
    except borrowers.DuplicateBorrowerError as e:
        print(f"\n✗ Error: {e}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Error creating borrower: {e}")


def update_fines_menu():
    """Menu option 5: Update fines."""
    print("\n--- Update Fines ---")
    
    try:
        print("Updating fines for all overdue loans...")
        fines.update_fines()
        print("\n✓ Fines updated successfully!")
        print("  All overdue loans have been processed.")
        
    except Exception as e:
        print(f"\n✗ Error updating fines: {e}")


def view_fines_menu():
    """Menu option 6: View fines."""
    print("\n--- View Fines ---")
    
    try:
        print("View fines:")
        print("1. For specific borrower (by Card ID)")
        print("2. For all borrowers")
        
        choice = input("\nEnter option (1-2): ").strip()
        
        card_id = None
        if choice == "1":
            card_id = input("Enter Borrower Card ID: ").strip()
            if not card_id:
                card_id = None
        
        include_paid_input = input("Include paid fines? (y/n, default=n): ").strip().lower()
        include_paid = include_paid_input == 'y'
        
        fine_summary = fines.get_fines_summary(card_id=card_id, include_paid=include_paid)
        
        if not fine_summary:
            if card_id:
                print(f"\nNo fines found for borrower Card ID {card_id}.")
            else:
                print("\nNo fines found.")
            return
        
        print(f"\n{'Borrower Name':<30} {'Card ID':<10} {'Total Fine':<15}")
        print("-" * 55)
        
        total_all_fines = 0
        for summary in fine_summary:
            fine_amount = float(summary['total_fine']) if summary['total_fine'] else 0.0
            total_all_fines += fine_amount
            print(f"{summary['borrower_name']:<30} {summary['card_id']:<10} ${fine_amount:.2f}")
        
        print("-" * 55)
        if len(fine_summary) > 1:
            print(f"{'TOTAL':<30} {'':<10} ${total_all_fines:.2f}")
        
        # Show payment option if there are unpaid fines
        if not include_paid and card_id:
            pay_choice = input(f"\nPay all fines for Card ID {card_id}? (y/n): ").strip().lower()
            if pay_choice == 'y':
                try:
                    fines.pay_all_fines(card_id)
                    print(f"\n✓ Successfully paid all fines for borrower {card_id}!")
                except fines.BooksStillOutError as e:
                    print(f"\n✗ Cannot pay fines: {e}")
                except Exception as e:
                    print(f"\n✗ Error paying fines: {e}")
        
    except Exception as e:
        print(f"\n✗ Error viewing fines: {e}")


def main():
    """Main CLI menu loop."""
    # Initialize database (create tables and import data if needed)
    init_db()
    
    print_header()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            search_books_menu()
        elif choice == "2":
            checkout_book_menu()
        elif choice == "3":
            checkin_book_menu()
        elif choice == "4":
            add_borrower_menu()
        elif choice == "5":
            update_fines_menu()
        elif choice == "6":
            view_fines_menu()
        elif choice == "7":
            print("\nThank you for using the Library Management System!")
            print("Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 7.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
