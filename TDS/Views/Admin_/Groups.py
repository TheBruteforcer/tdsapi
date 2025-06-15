from customtkinter import *
from PIL import Image
from sqlite3 import *

class GroupsView:
    def __init__(self, parent, db_name):
        self.parent = parent
        self.db_name = db_name
        self.conn = connect(db_name)
        self.ref = self.conn.cursor()
        self.setup_ui()

    def setup_ui(self):
        # Clear existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.create_header_frame()
        self.create_main_content()

    def create_header_frame(self):
        """Creates the header section with title and back button"""
        header = CTkFrame(self.parent, fg_color='white', corner_radius=20)
        header.pack(fill=X, padx=15, pady=10)

        # Groups icon
        groups_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(70, 70))
        CTkLabel(header, text='', image=groups_icon).pack(side=RIGHT, padx=10, pady=10)
        
        # Title
        CTkLabel(
            header, 
            text="إدارة المجموعات", 
            font=('Cairo Medium', 27)
        ).pack(side=RIGHT, padx=10, pady=(15,10))

        # Back button
        CTkButton(
            header,
            text='الرجوع الي الرئيسية',
            font=('Cairo Medium', 16),
            command=self.go_back,
            hover_color='#2B6BE6',
            height=45
        ).pack(side=LEFT, padx=10)

    def create_main_content(self):
        """Creates the main content area with group statistics"""
        main_frame = CTkScrollableFrame(self.parent, height=1000)
        main_frame.pack(padx=15, pady=10)

        # Debug: Print database connection info
        print(f"Database name: {self.db_name}")
        
        # Get all groups with their session times
        try:
            self.ref.execute('SELECT * FROM Groups')
            groups = self.ref.fetchall()
            print(f"Found groups: {groups}")  # Debug: Print groups
            
            if not groups:
                # If no groups found, show message
                CTkLabel(
                    main_frame,
                    text="لا توجد مجموعات",
                    font=('Cairo Medium', 20)
                ).pack(pady=20)
                return

            # Create grid layout
            row = 0
            col = 0
            for group in groups:
                print(f"\nProcessing group: {group}")  # Debug: Print current group
                
                try:
                    # Parse group name and time from the format "time | name"
                    group_info = group[0].split("|")
                    print(f"Group info split: {group_info}")  # Debug: Print split result
                    
                    group_time = group_info[0].strip()
                    group_name = group_info[1].strip() if len(group_info) > 1 else group[0]
                    print(f"Group time: {group_time}, Group name: {group_name}")  # Debug
                    
                    # Get group statistics
                    print(f"Getting statistics for group: {group[0]}")  # Debug
                    group_stats = self.get_group_statistics(group[0])
                    print(f"Statistics retrieved: {group_stats}")  # Debug
                    
                    # Create card for group
                    self.create_group_card(main_frame, group_name, group_time, group_stats, row, col)
                    
                    # Update grid position
                    col += 1
                    if col > 1:
                        col = 0
                        row += 1
                        
                except Exception as e:
                    print(f"Error processing group {group}: {str(e)}")  # Debug
                    continue

        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug
            CTkLabel(
                main_frame,
                text=f"خطأ في قاعدة البيانات: {str(e)}",
                font=('Cairo Medium', 16),
                text_color='red'
            ).pack(pady=20)

    def create_group_card(self, parent, group_name, group_time, stats, row, col):
        """Creates a detailed statistics card for a group"""
        card = CTkFrame(parent, fg_color='white', corner_radius=15)
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

        # Header with group name and time
        header = CTkFrame(card, fg_color='#2B6BE6', corner_radius=10)
        header.pack(fill=X, padx=5, pady=5)
        
        CTkLabel(
            header,
            text=f"{group_name}",
            font=('Cairo Medium', 24, 'bold'),
            text_color='white'
        ).pack(pady=(10,2))
        
        CTkLabel(
            header,
            text=f"الموعد: {group_time}",
            font=('Cairo Medium', 18),
            text_color='white'
        ).pack(pady=(0,10))

        # Main stats container
        main_stats = CTkFrame(card, fg_color='transparent')
        main_stats.pack(fill=X, padx=10, pady=10)

        # Left column - Basic Stats
        basic_stats = CTkFrame(main_stats, fg_color='transparent')
        basic_stats.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        self.create_stat_item(basic_stats, 
            "عدد الطلاب", 
            str(stats['students_count']),
            'TDSAssets/General/student3.png',
            0, 0
        )

        self.create_stat_item(basic_stats,
            "عدد الحصص",
            str(stats['sessions_count']),
            'TDSAssets/General/board.png',
            1, 0
        )

        # Right column - Financial Stats
        financial_stats = CTkFrame(main_stats, fg_color='transparent')
        financial_stats.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

        self.create_stat_item(financial_stats,
            "الإيرادات",
            f"{stats['total_revenue']:,} جنيه",
            'TDSAssets/General/green_money.png',
            0, 0
        )

        self.create_stat_item(financial_stats,
            "متوسط الإيراد للحصة",
            f"{stats['avg_revenue']:,} جنيه",
            'TDSAssets/General/green_money.png',
            1, 0
        )

        # Attendance section
        attendance_frame = CTkFrame(card, fg_color='#f8f9fa', corner_radius=10)
        attendance_frame.pack(fill=X, padx=10, pady=5)

        # Attendance rate with progress bar
        CTkLabel(
            attendance_frame,
            text="نسبة الحضور",
            font=('Cairo Medium', 18)
        ).pack(pady=(10,5))

        attendance_progress = CTkProgressBar(attendance_frame, height=15)
        attendance_progress.pack(fill=X, padx=15, pady=5)
        attendance_progress.set(stats['attendance_rate'] / 100)

        CTkLabel(
            attendance_frame,
            text=f"{stats['attendance_rate']}%",
            font=('Cairo Medium', 20, 'bold')
        ).pack(pady=5)

        # Additional statistics
        details_frame = CTkFrame(card, fg_color='transparent')
        details_frame.pack(fill=X, padx=10, pady=10)

        # Left column
        left_details = CTkFrame(details_frame, fg_color='transparent')
        left_details.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        CTkLabel(
            left_details,
            text=f"متوسط الحضور: {stats['avg_attendance']} طالب",
            font=('Cairo Medium', 14)
        ).pack(pady=2)

        CTkLabel(
            left_details,
            text=f"أعلى حضور: {stats['max_attendance']} طالب",
            font=('Cairo Medium', 14)
        ).pack(pady=2)

        # Right column
        right_details = CTkFrame(details_frame, fg_color='transparent')
        right_details.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

        CTkLabel(
            right_details,
            text=f"آخر حصة: {stats['last_session']}",
            font=('Cairo Medium', 14)
        ).pack(pady=2)

        CTkLabel(
            right_details,
            text=f"عدد الحصص هذا الشهر: {stats['sessions_this_month']}",
            font=('Cairo Medium', 14)
        ).pack(pady=2)

    def get_group_statistics(self, group_name):
        """Calculates detailed statistics for a group"""
        stats = {}
        
        try:
            # Basic stats
            self.ref.execute('SELECT COUNT(*) FROM Students WHERE Badges = ?', (group_name,))
            stats['students_count'] = self.ref.fetchone()[0]

            # Sessions data
            self.ref.execute('SELECT * FROM Sessions WHERE StartTime = ?', (group_name,))
            sessions = self.ref.fetchall()
            stats['sessions_count'] = len(sessions)
            
            # Financial calculations
            total_revenue = 0
            total_attendance = 0
            max_attendance = 0
            total_capacity = 0
            current_month_sessions = 0
            
            from datetime import datetime
            current_month = datetime.now().month
            
            for session in sessions:
                try:
                    attendance = int(session[4])
                    revenue = int(session[3]) * attendance
                    total_revenue += revenue
                    total_attendance += attendance
                    total_capacity += stats['students_count']
                    max_attendance = max(max_attendance, attendance)
                    
                    # Check if session is in current month
                    session_date = datetime.strptime(session[9], '%d \ %m \ %Y')
                    if session_date.month == current_month:
                        current_month_sessions += 1
                        
                except (ValueError, IndexError) as e:
                    continue

            # Calculate averages and rates
            stats['total_revenue'] = total_revenue
            stats['avg_revenue'] = round(total_revenue / stats['sessions_count']) if stats['sessions_count'] > 0 else 0
            stats['attendance_rate'] = round((total_attendance / total_capacity) * 100) if total_capacity > 0 else 0
            stats['avg_attendance'] = round(total_attendance / stats['sessions_count']) if stats['sessions_count'] > 0 else 0
            stats['max_attendance'] = max_attendance
            stats['sessions_this_month'] = current_month_sessions
            
            # Get latest session date
            stats['last_session'] = sessions[-1][9] if sessions else "لا يوجد"

        except Exception as e:
            print(f"Error calculating statistics: {str(e)}")
            stats = {
                'students_count': 0,
                'sessions_count': 0,
                'total_revenue': 0,
                'avg_revenue': 0,
                'attendance_rate': 0,
                'avg_attendance': 0,
                'max_attendance': 0,
                'sessions_this_month': 0,
                'last_session': "لا يوجد"
            }

        return stats

    def create_stat_item(self, parent, label, value, icon_path, row, col):
        """Creates a statistic item with icon and value"""
        frame = CTkFrame(parent, fg_color='#f8f9fa', corner_radius=10)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        icon = CTkImage(Image.open(icon_path), size=(24, 24))
        CTkLabel(frame, image=icon, text="").pack(pady=(5,0))
        
        CTkLabel(
            frame,
            text=value,
            font=('Cairo Medium', 18, 'bold')
        ).pack(pady=2)
        
        CTkLabel(
            frame,
            text=label,
            font=('Cairo Medium', 14)
        ).pack(pady=(0,5))

    def show_detailed_stats(self, group_name):
        """Shows detailed statistics for a group"""
        stats_window = CTkToplevel()
        stats_window.title(f"إحصائيات {group_name}")
        stats_window.geometry("800x600")

        # Create tabs for different statistics
        tabview = CTkTabview(stats_window)
        tabview.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Attendance tab
        attendance_tab = tabview.add("الحضور")
        self.create_attendance_stats(attendance_tab, group_name)

        # Revenue tab
        revenue_tab = tabview.add("الإيرادات")
        self.create_revenue_stats(revenue_tab, group_name)

        # Students tab
        students_tab = tabview.add("الطلاب")
        self.create_students_stats(students_tab, group_name)

    def go_back(self):
        """Handles navigation back to main admin view"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from Views.Admin import SuperUser
        SuperUser().UI(self.parent).pack(fill=BOTH, expand=True)

def GroupsSelectionView(parent):
    """Creates a selection view for choosing which grade's groups to manage"""
    for widget in parent.winfo_children():
        widget.destroy()

    # Create header frame
    header = CTkFrame(parent, fg_color='white', corner_radius=20)
    header.pack(fill=X, padx=15, pady=10)

    # Groups icon
    groups_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(70, 70))
    CTkLabel(header, text='', image=groups_icon).pack(side=RIGHT, padx=10, pady=10)
    
    # Title
    CTkLabel(
        header, 
        text="إدارة المجموعات", 
        font=('Cairo Medium', 27)
    ).pack(side=RIGHT, padx=10, pady=(15,10))

    # Back button
    def go_back():
        for widget in parent.winfo_children():
            widget.destroy()
        from Views.Admin import SuperUser
        SuperUser().UI(parent).pack(fill=BOTH, expand=True)

    CTkButton(
        header,
        text='الرجوع الي الرئيسية',
        font=('Cairo Medium', 16),
        command=go_back,
        hover_color='#2B6BE6',
        height=45
    ).pack(side=LEFT, padx=10)

    # Create main content area with full screen scrollable frame
    content_frame = CTkFrame(parent)
    content_frame.pack(fill=BOTH, expand=True)
    
    main_frame = CTkScrollableFrame(content_frame, height=1000)
    main_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)

    # Configure grid weights
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

    # Get all grades
    conn = connect("Application.db")
    ref = conn.cursor()
    ref.execute('SELECT * FROM PGroups')
    grades = ref.fetchall()

    # For each grade, get its groups and create cards
    for grade_index, grade in enumerate(grades):
        db_name = f"{grade[1]}.db"
        grade_conn = connect(db_name)
        grade_ref = grade_conn.cursor()
        
        # Get groups for this grade
        grade_ref.execute('SELECT * FROM Groups')
        groups = grade_ref.fetchall()
        
        # Create section title for grade
        grade_label = CTkFrame(main_frame, fg_color='#2B6BE6', corner_radius=10)
        grade_label.grid(row=grade_index*3, column=0, columnspan=2, sticky='ew', padx=15, pady=(20,10))
        CTkLabel(
            grade_label,
            text=grade[1],
            font=('Cairo Medium', 24, 'bold'),
            text_color='white'
        ).pack(pady=10)

        # Create cards for groups
        row = grade_index*3 + 1
        col = 0
        for group in groups:
            create_detailed_group_card(main_frame, group, grade_ref, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        grade_conn.close()
    conn.close()

def create_detailed_group_card(parent, group, ref, row, col):
    """Creates a detailed statistics card for a group"""
    card = CTkFrame(parent, fg_color='white', corner_radius=15)
    card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

    # Parse group name and time
    group_info = group[0].split("|")
    group_time = group_info[0].strip()
    group_name = group_info[1].strip() if len(group_info) > 1 else group[0]

    # Header with group name and time
    header = CTkFrame(card, fg_color='#2B6BE6', corner_radius=10)
    header.pack(fill=X, padx=5, pady=5)
    
    CTkLabel(
        header,
        text=group_name,
        font=('Cairo Medium', 24, 'bold'),
        text_color='white'
    ).pack(pady=(10,2))
    
    CTkLabel(
        header,
        text=f"الموعد: {group_time}",
        font=('Cairo Medium', 18),
        text_color='white'
    ).pack(pady=(0,10))

    # Get group statistics
    stats = get_detailed_group_stats(ref, group[0])

    # Main stats container
    stats_frame = CTkFrame(card, fg_color='transparent')
    stats_frame.pack(fill=X, padx=10, pady=10)

    # Left column
    left_stats = CTkFrame(stats_frame, fg_color='transparent')
    left_stats.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

    create_stat_item(left_stats,
        "عدد الطلاب",
        str(stats['students_count']),
        'TDSAssets/General/student3.png'
    )

    create_stat_item(left_stats,
        "عدد الحصص",
        str(stats['sessions_count']),
        'TDSAssets/General/board.png'
    )

    create_stat_item(left_stats,
        "متوسط الحضور",
        f"{stats['avg_attendance']} طالب",
        'TDSAssets/General/calender.png'
    )

    # Right column
    right_stats = CTkFrame(stats_frame, fg_color='transparent')
    right_stats.pack(side=RIGHT, fill=BOTH, expand=True, padx=5)

    create_stat_item(right_stats,
        "إجمالي الإيرادات",
        f"{stats['total_revenue']:,} جنيه",
        'TDSAssets/General/green_money.png'
    )

    create_stat_item(right_stats,
        "متوسط الإيراد للحصة",
        f"{stats['avg_revenue']:,} جنيه",
        'TDSAssets/General/green_money.png'
    )

    create_stat_item(right_stats,
        "حصص الشهر الحالي",
        str(stats['sessions_this_month']),
        'TDSAssets/General/board.png'
    )

    # Attendance progress section
    attendance_frame = CTkFrame(card, fg_color='#f8f9fa', corner_radius=10)
    attendance_frame.pack(fill=X, padx=10, pady=5)

    CTkLabel(
        attendance_frame,
        text="نسبة الحضور",
        font=('Cairo Medium', 18)
    ).pack(pady=(10,5))

    attendance_progress = CTkProgressBar(attendance_frame, height=15)
    attendance_progress.pack(fill=X, padx=15, pady=5)
    attendance_progress.set(stats['attendance_rate'] / 100)

    CTkLabel(
        attendance_frame,
        text=f"{stats['attendance_rate']}%",
        font=('Cairo Medium', 20, 'bold')
    ).pack(pady=5)

    # Last session info
    CTkLabel(
        card,
        text=f"آخر حصة: {stats['last_session']}",
        font=('Cairo Medium', 14)
    ).pack(pady=5)

def get_detailed_group_stats(ref, group_name):
    """Gets detailed statistics for a group"""
    stats = {}
    
    try:
        # Get students count (considering both direct group members and DroosIn)
        ref.execute('''
            SELECT COUNT(*) FROM Students 
            WHERE Badges = ? OR DroosIn LIKE ?
        ''', (group_name, f'%{group_name}%'))
        stats['students_count'] = ref.fetchone()[0]

        # Get sessions data
        ref.execute('SELECT * FROM Sessions WHERE StartTime = ?', (group_name,))
        sessions = ref.fetchall()
        stats['sessions_count'] = len(sessions)

        # Calculate statistics
        total_revenue = 0
        total_attendance = 0
        total_capacity = 0
        current_month_sessions = 0
        
        from datetime import datetime
        current_month = datetime.now().month
        
        for session in sessions:
            try:
                # Get total students for this session date
                session_date = datetime.strptime(session[9], '%d \ %m \ %Y')
                
                # Count students who were in the group at this session date
                ref.execute('''
                    SELECT COUNT(*) FROM Students 
                    WHERE Badges = ?
                ''', (group_name,))
                direct_students = ref.fetchone()[0]
                
                ref.execute('''
                    SELECT COUNT(*) FROM Students 
                    WHERE DroosIn LIKE ?
                ''', (f'%{group_name}%',))
                droosin_students = ref.fetchone()[0]
                
                session_capacity = direct_students + droosin_students
                attendance = int(session[4])
                revenue = int(session[3]) * attendance
                
                total_revenue += revenue
                total_attendance += attendance
                total_capacity += session_capacity
                
                # Check if session is in current month
                if session_date.month == current_month:
                    current_month_sessions += 1
            except Exception as e:
                print(f"Error processing session {session[0]}: {str(e)}")
                continue

        # Calculate final statistics
        stats['total_revenue'] = total_revenue
        stats['avg_revenue'] = round(total_revenue / stats['sessions_count']) if stats['sessions_count'] > 0 else 0
        stats['attendance_rate'] = round((total_attendance / total_capacity) * 100) if total_capacity > 0 else 0
        stats['avg_attendance'] = round(total_attendance / stats['sessions_count']) if stats['sessions_count'] > 0 else 0
        stats['sessions_this_month'] = current_month_sessions
        stats['last_session'] = sessions[-1][9] if sessions else "لا يوجد"

    except Exception as e:
        print(f"Error calculating statistics for {group_name}: {str(e)}")
        stats = {
            'students_count': 0,
            'sessions_count': 0,
            'total_revenue': 0,
            'avg_revenue': 0,
            'attendance_rate': 0,
            'avg_attendance': 0,
            'sessions_this_month': 0,
            'last_session': "لا يوجد"
        }

    return stats

def create_stat_item(parent, label, value, icon_path):
    """Creates a statistic item with icon"""
    frame = CTkFrame(parent, fg_color='#f8f9fa', corner_radius=10)
    frame.pack(fill=X, pady=5)

    icon = CTkImage(Image.open(icon_path), size=(24, 24))
    CTkLabel(frame, image=icon, text="").pack(side=RIGHT, padx=10, pady=5)
    
    CTkLabel(
        frame,
        text=label,
        font=('Cairo Medium', 14)
    ).pack(side=RIGHT, padx=5)
    
    CTkLabel(
        frame,
        text=value,
        font=('Cairo Medium', 16, 'bold')
    ).pack(side=LEFT, padx=10)

def Groups(parent):
    """Factory function to create the GroupsSelectionView"""
    return GroupsSelectionView(parent)
