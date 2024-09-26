let mainOBJ = [
  //array have all  Courses object
  {
    idSubject: "1", //Subject number #1
    CoursesName: "Oral and Maxillofacial Surgery III",
    level: "5",
    ch: "2",
    Instructors: [
      "خالد حسن مصطفى حسن",
      "سلمى عاطف صلاح الدين الشلقانى",
      "رودينا حسن السيد ابراهيم قطاريه",
      "منى عبدالمنعم محمد احمد عامر",
    ],
    Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Sunday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Wednesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Wednesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  }, // End Subject number #1

  {
    idSubject: "2", //Subject number #2
    CoursesName: "General Anesthesia and Basic Life Support",
    level: "5",
    ch: "3",
    Instructors: ["مشيره حامد ياسين عبد البر", "سلمى عاطف صلاح الدين الشلقانى"],
    Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on General Anesthesia and Basic Life Support
        sessionId: 1,
        Available: "33",
        day: "Saturday",
        FromTime: "14:45:00pm",
        toTime: "15:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "Hall C",
        Instructor: [
          "رزق عبدالله ابراهيم العجمي",
          "كريم علاء ابراهيم حسن ابراهيم",
        ],
        Status: "online",
      },
      {
        //  session #1 on General Anesthesia and Basic Life Support
        sessionId: 2,
        Available: "109",
        day: "Thursday",
        FromTime: "10:45:00pm",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "B",
        Facility: "Hall A",
        Instructor: [
          "رزق عبدالله ابراهيم العجمي",
          " ابراهيم حسن ابراهيم",
        ],
        Status: "online",
      }//End session #1
    ], // End all sessions array  on  Subject number #1
  },

  {
    idSubject: "3", //Subject number #3
    CoursesName: "Dental Anatomy and Occlusion 1",
    level: "5",
    ch: "3",
    Instructors: [" حامد ياسين عبد البر", " عاطف صلاح الدين الشلقانى"],
    Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Monday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Tuesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Tuesday",
        FromTime: "12:15:00am",
        toTime: "13:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },

  {
    idSubject: "4", //Subject number #4
    CoursesName: "Clinical Orthodontics I",
    level: "5",
    ch: "3",
    Instructors: ["  ياسين عبد البر", "  صلاح الدين الشلقانى"],
        Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Monday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Tuesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Tuesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },

  {
    idSubject: "5", //Subject number #5
    CoursesName: "General Physiology 1",
    level: "5",
    ch: "3",
    Instructors: [" حامد ياسين عبد البر", " عاطف صلاح الدين الشلقانى"],
        Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Sunday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Wednesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Wednesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },

  {
    idSubject: "6", //Subject number #6
    CoursesName: "Clinical Pediatric and Community ",
    level: "5",
    ch: "3",
    Instructors: [" حامد ياسين عبد البر", " عاطف صلاح الدين الشلقانى"],
        Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Sunday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Wednesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Wednesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },

  {
    idSubject: "7", //Subject number #7
    CoursesName: "Periodontology I ",
    level: "5",
    ch: "3",
    Instructors: [" حامد ياسين عبد البر"],
        Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Sunday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Wednesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Wednesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },

  {
    idSubject: "8", //Subject number #8
    CoursesName: "Clinical Removable Prosthodontics III ",
    level: "5",
    ch: "3",
    Instructors: [" عاطف صلاح الدين الشلقانى"],
        Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Sunday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Wednesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Wednesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },
  {
    idSubject: "9", //Subject number #9
    CoursesName: "Clinical Fixed Prosthodontics III ",
    level: "5",
    ch: "3",
    Instructors: [" حامد ياسين عبد البر", " عاطف صلاح الدين الشلقانى"],
        Sessions: [
      // all sessions With this Subject here
      {
        //  session #1 on  Oral and Maxillofacial Surger III
        sessionId: 1,
        Available: "48",
        day: "Sunday",
        FromTime: "10:45:00am",
        toTime: "11:45:00pm",
        type: "Lecture",
        Group: "A",
        Facility: "DT-online-3",
        Instructor:["رودينا حسن السيد ابراهيم قطاريه", "خالد حسن مصطفى حسن"] ,
        Status: "online",
      }, //End session #1

      {
        //  session #2 on  Oral and Maxillofacial Surger III
        sessionId: 2,
        Available: "170",
        day: "Wednesday",
        FromTime: "09:30:00am",
        toTime: "11:00:00am",
        type: "Lab",
        Group: "A1",
        Facility: "clinic4",
        Instructor: ["رزق عبدالله ابراهيم العجمي", " علاء ابراهيم حسن ابراهيم"],
        Status: "offline",
      }, //End session #2

      {
        //  session #3 on  Oral and Maxillofacial Surger III
        sessionId: 3,
        Available: "170",
        day: "Wednesday",
        FromTime: "11:15:00am",
        toTime: "12:45:00am",
        type: "Lab",
        Group: "A2",
        Facility: "clinic5",
        Instructor: ["رزق عبدالله ابراهيم العجمي", "خالد محمد شوقى على السيد "],
        Status: "offline",
      }, //End session #3
 

    ], // End all sessions array  on  Subject number #1
  },
  {
    idSubject: "10", //Subject number #10
    CoursesName: "Clinical Fixed Prosthodontics III  ",
    level: "5",
    ch: "3",
    Instructors: [" حامد  عبد البر", " عاطف الشلقانى"],
    Sessions: [],
  },
]; // End all array Subject

//define days to    fullCalendar
const fullCalendar_week = [
  { name: "saturday", value: 6 },
  { name: "sunday", value: 0 },
  { name: "monday", value: 1 },
  { name: "tuesday", value: 2 },
  { name: "wednesday", value: 3 },
  { name: "thursday", value: 4 },
  { name: "friday", value: 5 },
];
