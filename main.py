# main_app.py (updated with Taipo integration)

# Add import
from taipo_integration import TaipoIntegration

class PDFStudyApp:
    def __init__(self, root):
        # ... existing code ...
        self.taipo_integration = TaipoIntegration()
        
        # ... existing code ...
    
    def _setup_dashboard(self):
        # ... existing code ...
        
        # Add Taipo button
        taipo_btn = ttk.Button(button_frame, text="Launch Taipo", 
                              command=self._launch_taipo,
                              state=tk.DISABLED)
        taipo_btn.grid(row=0, column=4, padx=5)
        self.taipo_btn = taipo_btn
        
    def _open_pdf(self):
        # ... existing code ...
        
        # Enable Taipo button if we have items
        if self.study_items:
            self.taipo_btn.config(state=tk.NORMAL)
    
    def _launch_taipo(self):
        """Launch Taipo with current study items"""
        if not self.study_items:
            tk.messagebox.showinfo("No Study Items", "No study items available to send to Taipo.")
            return
        
        # First save the study content for Taipo
        try:
            # Generate a unique filename based on the PDF name
            pdf_name = self.pdf_path_var.get().replace("PDF: ", "").split(".")[0]
            filename = f"{pdf_name}_study"
            
            # Save the content
            content_file = self.taipo_integration.save_study_content(self.study_items, filename)
            
            # Launch Taipo
            success = self.taipo_integration.launch_taipo_with_study_content(content_file)
            
            if success:
                tk.messagebox.showinfo("Success", "Taipo launched successfully with your study content!")
            else:
                tk.messagebox.showerror("Error", "Failed to launch Taipo. Please check if it's installed correctly.")
        
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")