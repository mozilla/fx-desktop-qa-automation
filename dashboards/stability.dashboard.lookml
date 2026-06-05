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
    default_value: "mac,win"
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

  - name: Test
    title: Test
    type: field_filter
    model: stability_analytics
    explore: stability_test_events
    field: stability_test_events.test_nodeid
    allow_multiple_values: true
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

  - title: Top 10 Most Unstable Tests
    name: top_10_most_unstable_tests
    model: stability_analytics
    explore: stability_test_events
    type: looker_bar
    fields: [
      stability_test_events.test_nodeid,
      stability_test_events.failure_rate
    ]
    filters:
      stability_test_events.total_tests: ">=3"
    sorts: [stability_test_events.failure_rate desc]
    limit: 10
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed
      Platform: stability_test_events.platform

  - title: Monthly Failure Trend by Platform
    name: monthly_failure_trend_by_platform
    model: stability_analytics
    explore: stability_test_events
    type: looker_line
    fields: [
      stability_test_events.run_created_month,
      stability_test_events.platform,
      stability_test_events.failure_rate
    ]
    pivots: [stability_test_events.platform]
    sorts: [stability_test_events.run_created_month asc]
    limit: 500
    listen:
      Date: stability_test_events.run_created_month
      Headed: stability_test_events.headed
      Platform: stability_test_events.platform

  - title: Single-Test Stability Explorer
    name: single_test_stability_explorer
    model: stability_analytics
    explore: stability_test_events
    type: looker_line
    fields: [
      stability_test_events.run_created_date,
      stability_test_events.test_nodeid,
      stability_test_events.stability_rate
    ]
    pivots: [stability_test_events.test_nodeid]
    filters:
      stability_test_events.test_nodeid: "-NULL"
    sorts: [stability_test_events.run_created_date asc]
    limit: 500
    listen:
      Date: stability_test_events.run_created_date
      Headed: stability_test_events.headed
      Platform: stability_test_events.platform
      Test: stability_test_events.test_nodeid
