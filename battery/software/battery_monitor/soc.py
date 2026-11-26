"""State of charge: coulomb counting plus an open-circuit-voltage correction.

The OCV table is chemistry-specific and is supplied by the user. An empty
table disables the correction. Points are not extrapolated: a voltage outside
the table is ignored rather than turned into a guessed SOC.
"""

from __future__ import annotations


def ocv_to_soc(voltage_v: float, voltages: list[float], socs: list[float]) -> float | None:
    if len(voltages) < 2 or len(voltages) != len(socs):
        return None
    if voltage_v < voltages[0] or voltage_v > voltages[-1]:
        return None
    for index in range(len(voltages) - 1):
        v0 = voltages[index]
        v1 = voltages[index + 1]
        if v0 <= voltage_v <= v1:
            if v1 == v0:
                return None
            span = (voltage_v - v0) / (v1 - v0)
            return socs[index] + span * (socs[index + 1] - socs[index])
    return None


class RestTracker:
    """Tracks a continuous rest interval and applies OCV once per episode."""

    def __init__(self):
        self.elapsed_s = 0.0
        self._volt_sum = 0.0
        self._count = 0
        self.applied = False
        self.last_reason = ""

    def reset(self) -> None:
        self.elapsed_s = 0.0
        self._volt_sum = 0.0
        self._count = 0
        self.applied = False

    def update(
        self,
        state: dict,
        dt_s: float,
        current_a: float,
        voltage_v: float,
        profile: dict,
    ) -> bool:
        """Return True when an OCV correction is applied on this call."""
        from .profile import idle_threshold_a

        rest_current = profile.get("rest_current_a", None)
        if rest_current is None:
            rest_current = idle_threshold_a(profile)
        rest_current = float(rest_current)
        duration = float(profile.get("rest_duration_s", 300.0))
        if abs(current_a) > rest_current or dt_s < 0:
            self.reset()
            self.last_reason = "not at rest"
            return False
        self.elapsed_s += dt_s
        self._volt_sum += voltage_v
        self._count += 1
        if self.applied or self.elapsed_s < duration or self._count == 0:
            self.last_reason = "waiting" if not self.applied else "already applied this rest"
            return False
        voltages = [float(v) for v in profile.get("ocv_voltage_v") or []]
        socs = [float(s) for s in profile.get("ocv_soc_percent") or []]
        if len(voltages) < 2:
            self.last_reason = "no OCV table"
            self.applied = True
            return False
        mean_v = self._volt_sum / self._count
        soc = ocv_to_soc(mean_v, voltages, socs)
        if soc is None:
            self.last_reason = "voltage outside OCV table"
            self.applied = True
            return False
        state["soc_anchor_percent"] = soc
        state["ah_at_anchor"] = float(state.get("ampere_hours_out", 0.0))
        self.applied = True
        self.last_reason = "applied"
        return True
