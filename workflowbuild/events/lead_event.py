import frappe
from workflowbuild.schedule.execute_action import check_trigger_event
def after_save_all(doc, method):
    
    workflow_name = doc.custom_workflow
    frappe.logger().info(f"Workflow name: {workflow_name}")

    if workflow_name:
        workflow_data = frappe.get_doc('Workflow Configuration', workflow_name)
        
        print("workflow_Data",workflow_data)
        if workflow_data.trigger_event == "New Lead":
            workflow_actions = workflow_data.workflow_action
            workflow_actions_data = [
                frappe.get_doc('Workflow Actions', action.name).as_dict()
                for action in workflow_actions
            ]
            doc_dict = doc.as_dict()
            print(doc_dict)
            # Call the custom method
            try:
                
                res = check_trigger_event(workflow_actions_data, doc_dict)
                if res:
                    frappe.logger().info(f"Trigger Event API Response: {res}")
                else:
                    frappe.logger().warning("No response from Trigger Event API")
            except Exception as e:
                frappe.log_error(f"Error calling Trigger Event API: {str(e)}")

    