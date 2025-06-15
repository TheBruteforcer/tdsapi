from customtkinter import *
from PIL import Image
import requests
import threading
import datetime
from typing import Dict, List
import json
from tkinter import messagebox
import time

class ServiceStatusView:
    def __init__(self, parent: CTkFrame):
        self.parent = parent
        self.services_status: Dict[str, bool] = {}
        self.status_widgets: Dict[str, Dict] = {}
        self.is_monitoring = True
        
        # Service configurations
        self.services = {
            "whatsapp": {
                "name": "خدمة الواتساب",
                "url": "https://api.whatsapp.com/status",
                "icon": "whatsapp.png",
                "color": "#25D366",
                "description": "خدمة إرسال الرسائل والإشعارات"
            },
            "payment_gateway": {
                "name": "بوابة متابعة الطلاب",
                "url":"alawael-center.vercel.app",
                "icon": "student2.png",
                "color": "#FF6B6B",
                "description": "خدمة متابعة الطلاب عن بُعد "
            }
        }
        
        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        """Creates the main UI for service status monitoring"""
        # Clear existing widgets
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Header Section
        self.create_header_frame()
        
        # Main Content
        content_frame = CTkFrame(self.parent, fg_color="transparent")
        content_frame.pack(fill=BOTH, expand=True, padx=15, pady=10)
        
        # Status Overview
        self.create_status_overview(content_frame)
        
        # Detailed Status Cards
        self.create_status_cards(content_frame)
        
        # Activity Log
        self.create_activity_log(content_frame)

    def create_header_frame(self):
        """Creates the header section with title and back button"""
        header = CTkFrame(self.parent, fg_color='white', corner_radius=20)
        header.pack(fill=X, padx=15, pady=10)

        # Left side - Back button
        CTkButton(
            header,
            text='الرجوع الي الرئيسية',
            font=('Cairo Medium', 16),
            command=self.go_back,
            hover_color='#2B6BE6',
            height=45
        ).pack(side=LEFT, padx=10)

        # Right side - Title and Icon
        title_frame = CTkFrame(header, fg_color="transparent")
        title_frame.pack(side=RIGHT, fill=Y)

        status_icon = CTkImage(Image.open('TDSAssets/General/stats.png'), size=(70, 70))
        CTkLabel(title_frame, text='', image=status_icon).pack(side=RIGHT, padx=10, pady=10)
        
        title_text = CTkFrame(title_frame, fg_color="transparent")
        title_text.pack(side=RIGHT, pady=10, padx=10)
        
        CTkLabel(
            title_text, 
            text="حالة الخدمات", 
            font=('Cairo Medium', 24, "bold")
        ).pack(anchor="e")
        
        CTkLabel(
            title_text,
            text="مراقبة حالة الخدمات والأنظمة المتصلة",
            font=('Cairo Medium', 14),
            text_color="gray"
        ).pack(anchor="e")

    def create_status_overview(self, parent):
        """Creates the status overview section"""
        overview_frame = CTkFrame(parent, fg_color="white", corner_radius=15)
        overview_frame.pack(fill=X, pady=(0, 10))

        # Status Summary
        summary_frame = CTkFrame(overview_frame, fg_color="transparent")
        summary_frame.pack(fill=X, padx=20, pady=15)

        self.status_summary = CTkLabel(
            summary_frame,
            text="جميع الأنظمة تعمل بشكل طبيعي",
            font=("Cairo Medium", 18),
            text_color="#4CAF50"
        )
        self.status_summary.pack(side=RIGHT)

        # Last updated
        self.last_updated = CTkLabel(
            summary_frame,
            text="آخر تحديث: الآن",
            font=("Cairo Medium", 14),
            text_color="gray"
        )
        self.last_updated.pack(side=LEFT)

    def create_status_cards(self, parent):
        """Creates status cards for each service"""
        cards_frame = CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill=X, pady=5)

        for service_id, service_info in self.services.items():
            card = CTkFrame(cards_frame, fg_color="white", corner_radius=15)
            card.pack(fill=X, pady=5)

            # Service icon
            icon = CTkImage(
                Image.open(f'TDSAssets/General/{service_info["icon"]}'),
                size=(40, 40)
            )
            CTkLabel(card, image=icon, text="").pack(side=RIGHT, padx=15, pady=15)

            # Service info
            info_frame = CTkFrame(card, fg_color="transparent")
            info_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

            CTkLabel(
                info_frame,
                text=service_info["name"],
                font=("Cairo Medium", 16, "bold")
            ).pack(anchor="e")

            CTkLabel(
                info_frame,
                text=service_info["description"],
                font=("Cairo Medium", 12),
                text_color="gray"
            ).pack(anchor="e")

            # Status indicator
            status_frame = CTkFrame(card, fg_color="transparent")
            status_frame.pack(side=LEFT, padx=15, pady=15)

            status_indicator = CTkLabel(
                status_frame,
                text="جاري الفحص...",
                font=("Cairo Medium", 14),
                text_color="gray"
            )
            status_indicator.pack()

            # Store widgets for updating
            self.status_widgets[service_id] = {
                "indicator": status_indicator,
                "card": card
            }

    def create_activity_log(self, parent):
        """Creates the activity log section"""
        log_frame = CTkFrame(parent, fg_color="white", corner_radius=15)
        log_frame.pack(fill=BOTH, expand=True, pady=(10, 0))

        # Log header
        log_header = CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill=X, padx=20, pady=10)

        history_icon = CTkImage(Image.open('TDSAssets/General/calender.png'), size=(20, 20))
        CTkLabel(
            log_header,
            text="   سجل النشاط   ",
            font=("Cairo Medium", 16, "bold"),
            image=history_icon,
            compound="right"
        ).pack(side=RIGHT)

        # Log content
        self.log_content = CTkTextbox(
            log_frame,
            font=("Cairo Medium", 12),
            height=150,
            fg_color="transparent"
        )
        self.log_content.pack(fill=BOTH, expand=True, padx=20, pady=(0, 10))

    def check_service_status(self, service_id: str):
        """Checks the status of a specific service"""
        service = self.services[service_id]
        try:
            if service_id == "whatsapp":
                # For demo/testing purposes, simulate success
                # In production, replace with actual WhatsApp API call
                is_up = True
                
                # Actual API call would look something like:
                # response = requests.get(service["url"], timeout=5)
                # is_up = response.status_code == 200
            else:
                # Simulated status for other services
                is_up = True  # In real implementation, make actual API calls
            
            self.update_service_status(service_id, is_up)
            self.log_activity(f"تم فحص {service['name']}: {'متصل' if is_up else 'غير متصل'}")
            
        except Exception as e:
            self.update_service_status(service_id, False)
            self.log_activity(f"خطأ في فحص {service['name']}: {str(e)}")

    def update_service_status(self, service_id: str, is_up: bool):
        """Updates the UI for a service's status"""
        if not self.is_monitoring:
            return

        self.services_status[service_id] = is_up
        widgets = self.status_widgets[service_id]
        
        if is_up:
            status_text = "متصل"
            status_color = "#4CAF50"
            bg_color = "#E8F5E9"
        else:
            status_text = "غير متصل"
            status_color = "#F44336"
            bg_color = "#FFEBEE"

        widgets["indicator"].configure(text=status_text, text_color=status_color)
        widgets["card"].configure(fg_color=bg_color)
        
        # Update summary
        all_up = all(self.services_status.values())
        self.status_summary.configure(
            text="جميع الأنظمة تعمل بشكل طبيعي" if all_up else "بعض الخدمات غير متصلة",
            text_color="#4CAF50" if all_up else "#F44336"
        )
        
        # Update last checked time
        self.last_updated.configure(
            text=f"آخر تحديث: {datetime.datetime.now().strftime('%I:%M %p')}"
        )

    def log_activity(self, message: str):
        """Adds a message to the activity log"""
        timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
        self.log_content.insert("1.0", f"{timestamp} - {message}\n")

    def start_monitoring(self):
        """Starts the service monitoring"""
        self.is_monitoring = True
        for service_id in self.services:
            threading.Thread(
                target=self.check_service_status,
                args=(service_id,),
                daemon=True
            ).start()

    def refresh_status(self):
        """Manually refreshes all service statuses"""
        self.log_activity("جاري تحديث حالة جميع الخدمات...")
        for service_id in self.services:
            threading.Thread(
                target=self.check_service_status,
                args=(service_id,),
                daemon=True
            ).start()

    def stop_monitoring(self):
        """Stops the service monitoring"""
        self.is_monitoring = False

    def go_back(self):
        """Handles navigation back to main admin view"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        from Views.Admin import SuperUser
        SuperUser().UI(self.parent).pack(fill=BOTH, expand=True)

def show(parent: CTkFrame):
    """Shows the service status view"""
    ServiceStatusView(parent)