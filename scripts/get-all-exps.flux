import "influxdata/influxdb/v1"
v1.tagValues(
    bucket: "main",
    tag: "exp",
    predicate: (r) => true,
    start: -180d
)
