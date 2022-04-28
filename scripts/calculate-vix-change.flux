_start = from(bucket: "main")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "underlying")
  |> filter(fn: (r) => r["symbol"] == "$VIX.X")
  |> filter(fn: (r) => r["_field"] == "last")
  |> first()
  |> findColumn(
    fn: (key) => true,
    column: "_value"
  )

from(bucket: "main")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "underlying")
  |> filter(fn: (r) => r["symbol"] == "$VIX.X")
  |> filter(fn: (r) => r["_field"] == "last")
  |> last()
  |> map(fn: (r) => ({ r with "start": _start[0]}))
  |> map(fn: (r) => ({ r with _value: (r._value - r.start) / r.start}))
  |> drop(columns: ["start"])
  |> yield()
