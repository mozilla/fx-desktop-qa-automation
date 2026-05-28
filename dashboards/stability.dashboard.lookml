- dashboard: stability_dashboard
  title: Stability Test Dashboard
  layout: newspaper
  preferred_viewer: dashboards-next

  filters:
  - name: Platform
    title: Platform
    type: field_filter
    model: stability_analytics
    explore: stability_test_events
    field: stability_test_events.platform
    default_value: "mac, win"
    allow_multiple_values: true
    required: false

  - name: Date
    title: Date
    type: date_filter
    default_value: 30 days
    allow_multiple_values: true
    required: false

  - name: Headed
    title: Headed
    type: field_filter
    model: stability_analytics
    explore: stability_test_events
    field: stability_test_events.headed
    default_value: "No"
    allow_multiple_values: false
    required: false

  elements:
  - title: macOS Stability
    name: macos_stability
    model: stability_analytics
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
    model: stability_analytics
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

  - title: Per-Test Stability Over Time
    name: per_test_stability_over_time
    model: stability_analytics
    explore: stability_test_events
    type: looker_line
    fields: [
      stability_test_events.run_created_date,
      stability_test_events.platform,
      stability_test_events.test_name,
      stability_test_events.stability_rate
    ]
    pivots: [stability_test_events.platform, stability_test_events.test_name]
    sorts: [stability_test_events.run_created_date asc]
    limit: 500
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed
      Platform: stability_test_events.platform

  - title: Worst Flaky Tests
    name: worst_flaky_tests
    model: stability_analytics
    explore: stability_test_events
    type: looker_bar
    fields: [
      stability_test_events.platform,
      stability_test_events.test_nodeid,
      stability_test_events.failure_rate,
      stability_test_events.total_tests
    ]
    filters:
      stability_test_events.total_tests: ">=3"
    sorts: [stability_test_events.failure_rate desc]
    limit: 20
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed
      Platform: stability_test_events.platform

  - title: Failures by Test Over Time
    name: failures_by_test_over_time
    model: stability_analytics
    explore: stability_test_events
    type: looker_line
    fields: [
      stability_test_events.run_created_date,
      stability_test_events.platform,
      stability_test_events.test_name,
      stability_test_events.failed_tests
    ]
    pivots: [stability_test_events.platform, stability_test_events.test_name]
    sorts: [stability_test_events.run_created_date asc]
    limit: 500
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed
      Platform: stability_test_events.platform
