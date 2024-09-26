/* @odoo-module */

import { registry } from "@web/core/registry";

// Retrieve the existing 'display_notification' action
const originalDisplayNotification = registry.category("actions").get("display_notification");

if (originalDisplayNotification) {
    // Override the original action with custom functionality
    registry.category("actions").add("display_notification", async (env, params) => {
        // Call the original action
        originalDisplayNotification(env, params);

        // Custom logic after the notification is displayed
        console.log("Custom logic triggered after notification display");
        console.log(params.context.active_id);
        console.log(params.params.message);
        
        if (params.params.message.includes("Those session lines can't be created")) {
            console.log("There are missed session lines.");

            // Retrieve the ORM service from the environment
            const orm = env.services.orm;

            // Fetch the data using the ORM service
            try {
                const gen_obj = await orm.read("generate.time.table", [params.context.active_id], ["time_table_lines"]);
                
                if (gen_obj.length > 0) {
                    const session_lines = gen_obj[0].time_table_lines;  // Assign the fetched data
                    console.log("session_lines:", session_lines);

                    // Redirect to form view after showing notification
                    setTimeout(async () => {
                        try {
                            const actionService = env.services.action;
                            const action = {
                                type: 'ir.actions.act_window',
                                res_model: 'generate.time.table',
                                res_id: params.context.active_id,
                                view_mode: 'form',
                                views: [[false, 'form']],  // Specify the form view
                                target: 'new',  // Optionally remove this to test without modal window
                            };

                            console.log("Performing redirect action...");
                            console.log(action);

                            await actionService.doAction(action);
                            console.log("Redirect action completed successfully.");
                        } catch (error) {
                            console.error("Error performing redirect action:", error);
                        }
                    }, 50); // Delay to ensure the notification is shown
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        }
    }, { force: true }); // 'force: true' to force the override
}




// /* @odoo-module */

// import { registry } from "@web/core/registry";

// // Retrieve the existing 'display_notification' action
// const originalDisplayNotification = registry.category("actions").get("display_notification");

// if (originalDisplayNotification) {
//     // Override the original action with custom functionality
//     registry.category("actions").add("display_notification", async (env, params) => {
//         // Call the original action
//         originalDisplayNotification(env, params);

//         // Custom logic after the notification is displayed
//         console.log("Custom logic triggered after notification display");
//         console.log(params.context.active_id);
//         console.log(params.params.message);
        
//         if (params.params.message.includes("Those session lines can't be created")) {
//             console.log("There are missed session lines.");

//             // Retrieve the ORM service from the environment
//             const orm = env.services.orm;

//             // Fetch the data using the ORM service
//             try {
//                 const gen_obj = await orm.read("generate.time.table", [params.context.active_id], ["time_table_lines"]);
                
//                 if (gen_obj.length > 0) {
//                     const session_lines = gen_obj[0].time_table_lines;  // Assign the fetched data
//                     console.log("session_lines:", session_lines);
                    
//                     // Check for validation errors
//                     session_lines.forEach(line_id => {
//                         if (line_id.validation_error) {
//                             console.log(`Line ${line_id} has a validation error.`);
//                         }
//                     });

//                     // Trigger the UI to reload and reflect changes
//                     env.bus.trigger('reload');  // <-- Add this here
//                 }
//             } catch (error) {
//                 console.error("Error fetching data:", error);
//             }
//         }
//     }, { force: true }); // 'force: true' to force the override
// }
