# Frappe Project

This is a custom Frappe application designed to extend and enhance functionalities within the Frappe framework.

## 🚀 Getting Started

Follow the steps below to set up and run the project smoothly.

### 1. Get the App

```bash
bench get-app <repo-url>
```

### 2. Install the App on Your Site

Replace `your-site-name` with your actual site name:

```bash
bench --site your-site-name install-app workflowbuild
```

Then restart the bench:

```bash
bench restart
```

## ✅ Required Setup

To ensure smooth operation of the project, complete the following steps:

### 1. Add Worker with Scheduler in `Procfile`

In the **root directory of your Frappe bench**, open or create the `Procfile` and add the following line:

```
rq: rq worker --with-scheduler
```

### 2. Add Custom Field in Lead Doctype

Manually add a custom field to the **Lead** doctype:

- **Field Name:** `custom_workflow`
- **Label:** `Workflow`
- **Field Type:** Link (option: set options to `Workflow Configuration`)

Steps:

- Go to **Settings > Customization > Customize Form**
- Select **Doctype: Lead**
- Add a new field with the above specifications
- Save and reload

## 💡 Notes

- Ensure `bench start` or `bench start --watch` is running during development.
- Always restart the bench after installation or configuration changes:

```bash
bench restart
```
