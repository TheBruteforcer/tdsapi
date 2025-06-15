from sqlite3 import connect
from datetime import datetime
import os

class CustomGainsDB:
    def __init__(self):
        db_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(db_dir, "CustomGains.db")
        self.conn = connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()
    
    def setup_database(self):
        """Create all necessary tables if they don't exist"""
        # Table for programs, trips, and other custom gains
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Programs (
                ID          TEXT PRIMARY KEY,
                Title       TEXT NOT NULL,
                Type       TEXT NOT NULL,  -- 'رحلة', 'معسكر', 'برنامج', etc.
                Cost       REAL NOT NULL,
                StartDate  TEXT NOT NULL,
                EndDate    TEXT NOT NULL,
                MaxStudents INTEGER NOT NULL,
                Description TEXT,
                Location   TEXT NOT NULL,
                Status     TEXT DEFAULT 'active'  -- 'active', 'completed', 'cancelled'
            )
        """)
        
        # Table for registrations
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Registrations (
                ID         TEXT PRIMARY KEY,
                ProgramID  TEXT NOT NULL,
                StudentName TEXT NOT NULL,
                Phone      TEXT,
                ParentPhone TEXT,
                PaymentStatus TEXT DEFAULT 'pending',  -- 'pending', 'paid', 'cancelled'
                PaymentDate   TEXT,
                PaymentAmount REAL DEFAULT 0,
                Notes      TEXT,
                FOREIGN KEY (ProgramID) REFERENCES Programs(ID)
            )
        """)
        
        # Table for program updates/announcements
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ProgramUpdates (
                ID         TEXT PRIMARY KEY,
                ProgramID  TEXT NOT NULL,
                UpdateDate TEXT NOT NULL,
                Title      TEXT,
                Content    TEXT NOT NULL,
                Type       TEXT DEFAULT 'announcement',  -- 'announcement', 'schedule_change', 'cancellation', etc.
                FOREIGN KEY (ProgramID) REFERENCES Programs(ID)
            )
        """)

        # Table for Gains (additional income sources)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Gains (
                ID          TEXT PRIMARY KEY,
                Title       TEXT NOT NULL,
                Amount     REAL NOT NULL,
                Date       TEXT NOT NULL,
                Category   TEXT NOT NULL,
                Notes      TEXT,
                Status     TEXT DEFAULT 'completed'
            )
        """)

        # Table for Students (for quick registration)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Students (
                ID          TEXT PRIMARY KEY,
                Name        TEXT NOT NULL,
                Phone       TEXT,
                ParentPhone TEXT,
                Notes       TEXT,
                JoinDate    TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def add_program(self, title, type_, cost, start_date, end_date, max_students, description, location):
        """Add a new program"""
        try:
            program_id = f"PRG_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.cursor.execute("""
                INSERT INTO Programs (
                    ID, Title, Type, Cost, StartDate, EndDate,
                    MaxStudents, Description, Location, Status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (program_id, title, type_, cost, start_date, end_date,
                  max_students, description, location))
            self.conn.commit()
            return program_id
        except Exception as e:
            print(f"Error adding program: {str(e)}")
            raise
    
    def add_registration(self, program_id, student_name, phone, parent_phone, payment_amount=None, notes=None):
        """Register a student for a program"""
        reg_id = f"REG_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.cursor.execute("""
            INSERT INTO Registrations (ID, ProgramID, StudentName, Phone, ParentPhone, PaymentAmount, Notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (reg_id, program_id, student_name, phone, parent_phone, payment_amount, notes))
        self.conn.commit()
        return reg_id
    
    def get_active_programs(self):
        """Get all active programs"""
        try:
            self.cursor.execute("""
                SELECT * FROM Programs 
                WHERE Status = 'active' 
                ORDER BY StartDate DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting active programs: {str(e)}")
            return []
    
    def get_program_registrations(self, program_id):
        """Get all registrations for a specific program"""
        try:
            self.cursor.execute("""
                SELECT * FROM Registrations 
                WHERE ProgramID = ?
                ORDER BY PaymentDate DESC
            """, (program_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting program registrations: {str(e)}")
            return []
    
    def update_payment_status(self, registration_id, status, payment_date=None, payment_amount=None):
        """Update payment status for a registration"""
        if payment_date is None:
            payment_date = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute("""
            UPDATE Registrations 
            SET PaymentStatus = ?, PaymentDate = ?, PaymentAmount = ?
            WHERE ID = ?
        """, (status, payment_date, payment_amount, registration_id))
        self.conn.commit()
    
    def add_program_update(self, program_id, content, title=None):
        """Add an update to a program"""
        try:
            update_id = f"UPD_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            update_date = datetime.now().strftime('%Y-%m-%d')
            
            self.cursor.execute("""
                INSERT INTO ProgramUpdates (
                    ID, ProgramID, UpdateDate, Title, Content
                ) VALUES (?, ?, ?, ?, ?)
            """, (update_id, program_id, update_date, title, content))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding program update: {str(e)}")
            return False
    
    def get_program_updates(self, program_id):
        """Get all updates for a specific program"""
        try:
            self.cursor.execute("""
                SELECT * FROM ProgramUpdates 
                WHERE ProgramID = ?
                ORDER BY UpdateDate DESC
            """, (program_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting program updates: {str(e)}")
            return []
    
    def __del__(self):
        """Destructor to ensure database connection is closed"""
        try:
            self.conn.close()
        except:
            pass

    def get_total_registrations(self):
        """Get total number of registrations across all programs"""
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM Registrations
            """)
            total = self.cursor.fetchone()[0]
            return total
        except Exception as e:
            print(f"Error getting total registrations: {str(e)}")
            return 0

    def get_total_revenue(self):
        """Get total revenue from all registrations"""
        try:
            self.cursor.execute("""
                SELECT SUM(PaymentAmount) FROM Registrations
                WHERE PaymentStatus = 'paid'
            """)
            total = self.cursor.fetchone()[0] or 0

            # Also get revenue from Gains table
            self.cursor.execute("""
                SELECT SUM(Amount) FROM Gains
                WHERE Status = 'completed'
            """)
            gains_total = self.cursor.fetchone()[0] or 0

            return total + gains_total
        except Exception as e:
            print(f"Error getting total revenue: {str(e)}")
            return 0

    def get_all_programs(self):
        """Get all programs for reporting"""
        try:
            self.cursor.execute("""
                SELECT * FROM Programs
                ORDER BY StartDate DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all programs: {str(e)}")
            return []

    def get_program_details(self, program_id):
        """Get detailed information about a specific program"""
        try:
            self.cursor.execute("""
                SELECT * FROM Programs
                WHERE ID = ?
            """, (program_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting program details: {str(e)}")
            return None

    def register_student(self, program_id, name, phone, parent_phone, amount_paid):
        """Register a student for a program"""
        try:
            reg_id = f"REG_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            payment_date = datetime.now().strftime('%Y-%m-%d')
            
            self.cursor.execute("""
                INSERT INTO Registrations (
                    ID, ProgramID, StudentName, Phone,
                    ParentPhone, PaymentAmount, PaymentDate, PaymentStatus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (reg_id, program_id, name, phone, parent_phone, 
                  amount_paid, payment_date, 'paid' if amount_paid > 0 else 'pending'))
            
            # Also add to Students table if not exists
            self.cursor.execute("""
                INSERT OR IGNORE INTO Students (
                    ID, Name, Phone, ParentPhone, JoinDate
                ) VALUES (?, ?, ?, ?, ?)
            """, (f"STD_{name}_{phone}", name, phone, parent_phone, payment_date))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error registering student: {str(e)}")
            return False

# Create a global instance
custom_gains_db = CustomGainsDB() 