view: stability_test_events {
  # # You can specify the table name if it's different from the view name:
  # sql_table_name: my_schema_name.tester ;;
  #
  # # Define your dimensions and measures here, like this:
  # dimension: user_id {
  #   description: "Unique ID for each user that has ordered"view: stability_test_events {
  sql_table_name: `moz-desktop.stability.stability_test_events` ;;

  dimension: run_id {
    type: number
    sql: ${TABLE}.run_id ;;
  }

  dimension: run_number {
    type: number
    sql: ${TABLE}.run_number ;;
  }

  dimension_group: run_created {
    type: time
    timeframes: [raw, date, week, month]
    sql: ${TABLE}.run_created_at ;;
  }

  dimension_group: ingested {
    type: time
    timeframes: [raw, date, week, month]
    sql: ${TABLE}.ingested_at ;;
  }

  dimension: platform {
    type: string
    sql: ${TABLE}.platform ;;
  }

  dimension: headed {
    type: yesno
    sql: ${TABLE}.headed ;;
  }

  dimension: artifact_name {
    type: string
    sql: ${TABLE}.artifact_name ;;
  }

  dimension: test_nodeid {
    type: string
    sql: ${TABLE}.test_nodeid ;;
  }

  dimension: outcome {
    type: string
    sql: ${TABLE}.outcome ;;
  }

  dimension: duration {
    type: number
    sql: ${TABLE}.duration ;;
  }

  measure: total_tests {
    type: count
  }

  measure: passed_tests {
    type: count
    filters: [outcome: "passed"]
  }

  measure: failed_tests {
    type: count
    filters: [outcome: "failed"]
  }

  measure: stability_rate {
    type: number
    value_format_name: percent_2
    sql: SAFE_DIVIDE(${passed_tests}, NULLIF(${total_tests}, 0)) ;;
  }

  measure: avg_duration {
    type: average
    value_format_name: decimal_2
    sql: ${duration} ;;
  }
}
