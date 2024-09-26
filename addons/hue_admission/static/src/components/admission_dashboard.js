odoo.define('admission_dashboard.Dashboard', function(require) {
    "use strict";
    var AbstractAction = require("web.AbstractAction");
    var core = require('web.core');
    
    var HrDashboard = AbstractAction.extend({
        template: "HrDashboardMain",
        events: {
            'click .open_app': 'open_application',
        },
        
        init: function(parent, context) {
            this._super(parent, context);
            this.admission_data = false;
            this.action_id = context.id;
            this._super(parent, context);
        },
        
        
        //start: function() {
        //    var self = this;
        //    for (var i in self.breadcrumbs) {
        //        self.breadcrumbs[i].title = "Dashboard";
        //    }
        //    self.update_control_panel({
        //        breadcrumbs: self.breadcrumbs
        //    }, {
        //        clear: true
        //    });
        //    rpc.query({
        //        model: "op.admission",
        //        method: "get_admission_details",
        //    })
        //        .then(function(result) {
        //        if (result) {
        //            self.admission_data = result;
        //            $('.o_hr_dashboard').prepend(QWeb.render('LoginEmployeeDetails', {
        //                widget: self
        //            }));
        //            /*need to check user access levels*/
        //            //#self.render_graph();
        //            self.graph();
        //            self.previewTable();
        //            session.user_has_group('hr.group_hr_manager').then(function(has_group) {
        //                if (has_group == false) {
        //                    $('.employee_dashboard_main').css("display", "none");
        //                }
        //            });
        //
        //
        //        } else {
        //            $('.o_hr_dashboard').html(QWeb.render('EmployeeWarning', {
        //                widget: self
        //            }));
        //            return;
        //        }
        //    });
        //},
        //on_reverse_breadcrumb: function() {
        //    this.update_control_panel({clear: true});
        //    alert(this.action_id);
        //    //web_client.do_push_state({action: this.action_id});
        //},
        //
        //open_application: function(event) {
        //    var self = this;
        //    var id = event.currentTarget.id;
        //    event.stopPropagation();
        //    event.preventDefault();
        //    var options = {
        //        on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        //    };            
        //    var daat = this.do_action({
        //        name: _t("Admission"),
        //        type: 'ir.actions.act_window',
        //        res_model: 'op.admission',
        //        res_id: parseInt(id),
        //        view_mode: 'form',
        //        view_type: 'form',
        //        views: [[false, 'form']],
        //        context: {},
        //        domain: [],
        //        target: 'new'
        //    }, options)
        //    
        //},
        //get_emp_image_url: function(employee) {
        //    return window.location.origin + '/web/image?model=hr.employee&field=image&id=' + employee;
        //},
        //get_admission_applicant: function(admission_register, type) {
        //    this._rpc({
        //        model: 'op.admission.register',
        //        method: 'get_admission_applicant',
        //        args: [admission_register, type],
        //    })
        //        .then(function(result) {
        //        alert(result);
        //        return result;
        //    });
        //},
        //generate_broad_factor_report: function() {
        //    this.do_action({
        //        type: 'ir.actions.report',
        //        report_type: 'qweb-pdf',
        //        report_name: 'hrms_dashboard.report_broadfactor/1'
        //    });
        //},
        //
        //// datatables
        //previewTable: function() {
        //    $('#emp_details').DataTable( {
        //        buttons: [
        //            {
        //                extend: 'print',
        //                exportOptions: {
        //                columns: ':visible'
        //                }
        //            },
        //        
        //        ],
        //    } );
        //    $('#candidate_tb').DataTable( {
        //        buttons: [
        //            {
        //                extend: 'print',
        //                exportOptions: {
        //                columns: ':visible'
        //                }
        //            },
        //        ],
        //    } );
        //    $('#enrolled_tb').DataTable( {
        //        buttons: [
        //            {
        //                extend: 'print',
        //                exportOptions: {
        //                columns: ':visible'
        //                }
        //            },
        //        ],
        //    } );             
        //},
        //// Here we are plotting bar,pie chart
        //graph: function() {
        //    var self = this;
        //    var ctx = this.$el.find('#myChart');
        //    
        //    var Registeredbyfaculty = this.$el.find('#Registeredbyfaculty');
        //    
        //    // Candidate chart
        //    var Candidatebycertificate = this.$el.find('#Candidatebycertificate');
        //    var ctxCandidatefaculty = this.$el.find('#Candidatebyfaculty');
        //    var ctxCandidateNationality = this.$el.find('#CandidatebyNationality');
        //    // Enrolled Chart
        //    var Enrolledbycertificate = this.$el.find('#Enrolledbycertificate');
        //    var ctxEnrolledfaculty = this.$el.find('#Enrolledbyfaculty');
        //    var ctxEnrolledNationality = this.$el.find('#EnrolledbyNationality');            
        //    // Fills the canvas with white background
        //    Chart.plugins.register({
        //        beforeDraw: function(chartInstance) {
        //            var ctx = chartInstance.chart.ctx;
        //            ctx.fillStyle = "white";
        //            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
        //        }
        //    });
        //
        //    new Chart(ctx, {
        //        type: 'bar',
        //        options: {
        //            title: {
        //                display: true,
        //                text: 'Admission Application Status',
        //                fontSize: 20,
        //
        //            },
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.admission_register_label,
        //            datasets: [{
        //                    label: "Applicant (المتقدمين)",
        //                    backgroundColor: "pink",
        //                    borderColor: "red",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_applicants
        //                }, {
        //                    label: "Candidate (المرشحون)",
        //                    backgroundColor: "lightblue",
        //                    borderColor: "blue",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_candidate
        //                }, {
        //                    label: "Enrolled (المقبولين)",
        //                    backgroundColor: "#9de6d8",
        //                    borderColor: "#267b6a",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_enrolled
        //                },
        //
        //            ]
        //        },
        //
        //    });
        //    
        //    
        //     // Candidate chart
        //    var Candidatebycertificate = this.$el.find('#Candidatebycertificate');
        //    var ctxCandidatefaculty = this.$el.find('#Candidatebyfaculty');
        //    var ctxCandidateNationality = this.$el.find('#CandidatebyNationality');
        //    // Enrolled Chart
        //    var Enrolledbycertificate = this.$el.find('#Enrolledbycertificate');
        //    var ctxEnrolledfaculty = this.$el.find('#Enrolledbyfaculty');
        //    var ctxEnrolledNationality = this.$el.find('#EnrolledbyNationality');            
        //    // Fills the canvas with white background
        //    Chart.plugins.register({
        //        beforeDraw: function(chartInstance) {
        //            var ctx = chartInstance.chart.ctx;
        //            ctx.fillStyle = "white";
        //            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
        //        }
        //    });
        //
        //    new Chart(ctx, {
        //        type: 'bar',
        //        options: {
        //            title: {
        //                display: true,
        //                text: 'Admission Application Status',
        //                fontSize: 20,
        //
        //            },
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.admission_register_label,
        //            datasets: [{
        //                    label: "Applicant (المتقدمين)",
        //                    backgroundColor: "pink",
        //                    borderColor: "red",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_applicants
        //                }, {
        //                    label: "Candidate (المرشحون)",
        //                    backgroundColor: "lightblue",
        //                    borderColor: "blue",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_candidate
        //                }, {
        //                    label: "Enrolled (المقبولين)",
        //                    backgroundColor: "#9de6d8",
        //                    borderColor: "#267b6a",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_enrolled
        //                },
        //
        //            ]
        //        },
        //
        //    });
        //    
        //    // Enrolled charts  //////////////////////////////////////////////////
        //    //Enrolled  Chart
        //    new Chart(Enrolledbycertificate, {
        //        type: 'bar',
        //        options: {
        //            responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.certificate_label,
        //            datasets: self.admission_data.enrolled_data
        //        },
        //
        //    });
        //    //Candidate NAtionality  Chart
        //    new Chart(ctxEnrolledNationality, {
        //        type: 'bar',
        //        options: {
        //            responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.nationality_label,
        //            datasets: self.admission_data.enrolled_nationality_data
        //        },
        //
        //    });
        //    
        //    
        //    //candidate by faculty
        //     new Chart(ctxEnrolledfaculty, {
        //        type: 'bar',
        //        options: {
        //             responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.admission_register_label,
        //            datasets: [{
        //                    label: "Candidate (المرشحون)",
        //                    backgroundColor: "pink",
        //                    borderColor: "red",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_enrolled
        //                }
        //
        //            ]
        //        },
        //
        //    });           
        //    // Candidate charts  //////////////////////////////////////////////////
        //    //Certificate  Chart
        //    new Chart(Candidatebycertificate, {
        //        type: 'bar',
        //        options: {
        //            responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.certificate_label,
        //            datasets: self.admission_data.certificate_data
        //        },
        //
        //    });
        //    //Candidate NAtionality  Chart
        //    new Chart(ctxCandidateNationality, {
        //        type: 'bar',
        //        options: {
        //            responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.nationality_label,
        //            datasets: self.admission_data.nationality_data
        //        },
        //
        //    });
        //    
        //    
        //    //candidate by faculty
        //     new Chart(ctxCandidatefaculty, {
        //        type: 'bar',
        //        options: {
        //             responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.admission_register_label,
        //            datasets: [{
        //                    label: "Candidate (المرشحون)",
        //                    backgroundColor: "pink",
        //                    borderColor: "red",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_candidate
        //                }
        //
        //            ]
        //        },
        //
        //    });
        //     
        //     // registred by faculy
        //    new Chart(Registeredbyfaculty, {
        //        type: 'bar',
        //        options: {
        //             responsive: true,
        //            scales: {
        //                yAxes: {
        //                    fontColor: 'black',
        //                    fontColor: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            },
        //            tooltips: {
        //
        //                // This more specific font property overrides the global property
        //                titleFontColor: 'white',
        //                titleFontSize: 14,
        //                titleFontStyle: "normal",
        //                titleFontFamily: "Verdana",
        //                backgroundColor: 'black',
        //                bodyFontColor: 'white',
        //                bodyFontSize: 14,
        //                bodyFontStyle: "normal",
        //                bodyFontFamily: "Verdana",
        //
        //            },
        //            legend: {
        //                labels: {
        //                    // This more specific font property overrides the global property
        //                    fontColor: 'black',
        //                    defaultFontSize: 14,
        //                    fontweight: "normal",
        //                    fontFamily: "Verdana",
        //                }
        //            }
        //        },
        //        data: {
        //            labels: self.admission_data.admission_register_label,
        //            datasets: [{
        //                    label: "Candidate (المرشحون)",
        //                    backgroundColor: "pink",
        //                    borderColor: "red",
        //                    borderWidth: 1,
        //                    data: self.admission_data.total_admission_register_applicants
        //                }
        //
        //            ]
        //        },
        //
        //    });
        //},
        
    });
    core.action_registry.add("admission_dashboard", HrDashboard);
    return HrDashboard;
});