connection: "telemetry"

include: "/views/*.view.lkml"
include: "/dashboards/*.dashboard.lookml"

explore: stability_test_events {
  label: "Stability Test Events"
}
