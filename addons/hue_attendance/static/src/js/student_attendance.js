/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class BarcodeAttendanceComponent extends Component {
    setup() {
        // Get context from the action
        const context = this.props.action.context || {};
        this.attendanceSheetId = context.attendance_sheet_id;
        this.sessionId = context.session_id;

        console.log("Attendance Sheet ID:", this.attendanceSheetId);
        console.log("Session ID:", this.sessionId);

        // Initialize services
        this.orm = useService("orm");
        this.notification = useService("notification");

        // Set up barcode scanning service and event listener with debouncing
        this.lastScanTime = 0;
        const barcode = useService("barcode");
        useBus(barcode.bus, "barcode_scanned", this.onBarcodeScanned.bind(this));

        console.log("Barcode listener set up successfully.");
    }

    async onBarcodeScanned(event) {
        const currentTime = new Date().getTime();
        
        // Debounce barcode scanning
        if (currentTime - this.lastScanTime < 1000) {  // 1 second debounce
            console.log("Barcode scan ignored due to debounce.");
            return;
        }
        this.lastScanTime = currentTime;

        console.log("Barcode scanned event triggered.");  // Debugging line
        const barcode = event.detail.barcode;
        console.log("Scanned Barcode:", barcode);

        if (!barcode) return;

        try {
            console.log("Fetching session students...");

            // Declare the session_students variable
            let session_students = [];
            let barcode_student;
            let taken_lines = [];
            let taken_students = [];

            // Fetch session students
            const session_students_records = await this.orm.read("op.session", [this.sessionId], ["student_ids"]);
            if (session_students_records.length > 0){
                session_students = session_students_records[0].student_ids;  // Assign the fetched data
                console.log("Session Students:", session_students);
            }
            
            
            // Fetch attendance sheet 
            console.log("Fetching attendance sheet...");
            const records = await this.orm.read("op.attendance.sheet", [this.attendanceSheetId], ["session_id","attendance_line"]);
            if (records.length > 0){
                this.attendanceSheet = records[0];
                console.log("Fetched Attendance Sheet:", this.attendanceSheet);
                // Fetch Taken lines
                taken_lines = records[0].attendance_line
                console.log("Fetched Attendance lines:", taken_lines);
            }
            
            
            // Fetch student_ids from taken_lines
            if (taken_lines.length > 0) {
                const attendance_line_records = await this.orm.read("op.attendance.line", taken_lines, ["student_id"]);
                taken_students = attendance_line_records.map(line => line.student_id[0]); // Extract student_id and store in array
                console.log("Taken Students (student_ids):", taken_students);
            } else {
                console.log("No attendance lines found.");
            }

            // Search and Fetch barcode student
            const barcode_student_record = await this.orm.searchRead("op.student", [['student_code', '=', barcode]], ["id", "name"]);
            barcode_student = barcode_student_record[0];

            if (!barcode_student) {
                // If barcode_student doesn't exist
                this.notification.add(`This ID is not registered.`, { type: "danger" });
                return;
            }

            // If barcode_student exists, check in session_students
            if (!session_students.includes(barcode_student.id)) {
                // If barcode_student is not part of session_students
                this.notification.add(`This ID is not registered for this session.`, { type: "danger" });
                return;
            }

            // If barcode_student is part of session_students, check in taken_students
            if (taken_students.includes(barcode_student.id)) {
                // If attendance already taken for this student
                this.notification.add(`Attendance for this student has already been taken.`, { type: "warning" });
            } else {
                // If attendance is not taken yet
                // Mark attendance by creating an attendance record
                const attendanceData = {
                    student_id: barcode_student.id,
                    attendance_id: this.attendanceSheetId,
                };
                await this.orm.create("op.attendance.line", [attendanceData]);
                this.notification.add(`Attendance for this ID taken successfully.`, { type: "success" });
                // Here, you can also add the logic to mark attendance if needed
            }
            
        } catch (error) {
            console.error("Error during attendance recording:", error);
            this.notification.add(`Error during attendance recording: ${error.message}`, { type: "danger" });
        } finally {
            console.log("Clearing input for the next scan.");
            event.detail.barcode = "";  // Clear the barcode input
        }
    }
}

BarcodeAttendanceComponent.template = "hue_attendance.BarcodeAttendanceComponent";

// Register the component
registry.category("actions").add("barcode_attendance_component", BarcodeAttendanceComponent);
