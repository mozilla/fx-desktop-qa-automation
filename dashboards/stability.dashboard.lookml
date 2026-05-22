- dashboard: stability_dashboard
  title: Stability Test Dashboard
  layout: newspaper
  preferred_viewer: dashboards-next

  filters:
  - name: Date
    title: Date
    type: date_filter
    default_value: 30 days
    allow_multiple_values: true
    required: false

  - name: Headed
    title: Headed
    type: field_filter
    model: stability
    explore: stability_test_events
    field: stability_test_events.headed
    default_value: "No"
    allow_multiple_values: false
    required: false

  elements:
  - title: macOS Stability
    name: macos_stability
    model: stability
    explore: stability_test_events
    type: looker_line
    fields: [
      stability_test_events.run_created_date,
      stability_test_events.stability_rate
    ]
    filters:
      stability_test_events.platform: "mac"
    sorts: [stability_test_events.run_created_date asc]
    limit: 500
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed

  - title: Windows Stability
    name: windows_stability
    model: stability
    explore: stability_test_events
    type: looker_line
    fields: [
      stability_test_events.run_created_date,
      stability_test_events.stability_rate
    ]
    filters:
      stability_test_events.platform: "win"
    sorts: [stability_test_events.run_created_date asc]
    limit: 500
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed
