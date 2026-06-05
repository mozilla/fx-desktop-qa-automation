view: stability_test_events {
  sql_table_name: `moz-desktop.stability.stability_test_events` ;;

  dimension: row_id {
    primary_key: yes
    hidden: yes
    type: string
    sql: CONCAT(
          CAST(${TABLE}.run_id AS STRING),
          '|',
          ${TABLE}.artifact_name,
          '|',
          ${TABLE}.test_nodeid
        ) ;;
  }

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
    datatype: timestamp
    timeframes: [raw, date, week, month]
    sql: SAFE_CAST(${TABLE}.run_created_at AS TIMESTAMP) ;;
  }

  dimension_group: ingested {
    type: time
    datatype: timestamp
    timeframes: [raw, date, week, month]
    sql: SAFE_CAST(${TABLE}.ingested_at AS TIMESTAMP) ;;
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

  dimension: test_file {
    type: string
    sql: SPLIT(${TABLE}.test_nodeid, '::')[SAFE_OFFSET(0)] ;;
  }

  dimension: test_name {
    type: string
    sql: ARRAY_REVERSE(SPLIT(${TABLE}.test_nodeid, '::'))[SAFE_OFFSET(0)] ;;
  }

  dimension: failed {
    type: yesno
    sql: ${TABLE}.outcome = 'failed' ;;
  }

  dimension: passed {
    type: yesno
    sql: ${TABLE}.outcome = 'passed' ;;
  }

  measure: failure_rate {
    type: number
    value_format_name: percent_2
    sql: SAFE_DIVIDE(${failed_tests}, NULLIF(${total_tests}, 0)) ;;
  }

  measure: unique_runs {
    type: count_distinct
    sql: ${TABLE}.run_id ;;
  }

  measure: unique_tests {
    type: count_distinct
    sql: ${TABLE}.test_nodeid ;;
  }

  measure: flaky_score {
    type: number
    value_format_name: percent_2

    # Flaky = both passes and fails observed.
    # Tests that always pass or always fail are not considered flaky.
    sql:
    CASE
      WHEN ${passed_tests} > 0 AND ${failed_tests} > 0
      THEN SAFE_DIVIDE(${failed_tests}, ${total_tests})
      ELSE 0
    END ;;
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
