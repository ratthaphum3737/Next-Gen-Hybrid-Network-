"""
simulation.py
=============
Module 2: Link Delay & Disruption Engine — จำลองสถานการณ์การสื่อสารอวกาศ

Sprint Beta Sprint 3 Fixes:
  ISS-01: เพิ่ม loss_rate บน link — P1 Critical bypass drop เสมอ
  ISS-02: is_online setter auto-flush buffer อัตโนมัติ

วิธีรัน:
  python simulation.py
"""

import time
from space_node import SpaceNode


def run_simulation():
    print("=" * 60)
    print("  🛰️  IDMS — Interstellar Data Mesh Simulation")
    print("       DTN + QoS + Packet Loss Guard Demo")
    print("=" * 60)

    # สร้างโหนดอวกาศ 4 ตัว (รองรับ AC-1: ≥3 nodes)
    # ISS-01: กำหนด loss_rate=0.5 (50%) บน earth link เพื่อทดสอบ P1 bypass
    earth   = SpaceNode("Earth Mission Control", loss_rate=0.5)
    lunar   = SpaceNode("Lunar Gateway Relay")
    surface = SpaceNode("Surface Base LAN")
    probe   = SpaceNode("Deep Space Probe")

    # ══════════════════════════════════════════════════════
    # สถานการณ์ที่ 1: สัญญาณปกติ — ทุกโหนด Online (TC-01)
    # ══════════════════════════════════════════════════════
    print("\n─── [TC-01: สัญญาณชัดเจน — ทุกโหนด Online] ───")
    earth.send_data(lunar,   "ตรวจสอบระบบนำทาง",       priority=1, label="Critical")
    earth.send_data(lunar,   "ภาพถ่ายพื้นผิวดวงจันทร์", priority=2, label="Scientific")
    earth.send_data(surface, "Telemetry Status",         priority=2, label="Scientific")
    earth.send_data(probe,   "Weekly Media Update",      priority=3, label="Media")
    time.sleep(0.3)

    # ══════════════════════════════════════════════════════
    # สถานการณ์ที่ 2: Packet Loss + P1 Critical Guard (ISS-01)
    # ══════════════════════════════════════════════════════
    print("\n─── [TC-01/ISS-01: Packet Loss 50% — P1 Critical ต้องไม่ถูก Drop] ───")
    print(f"     loss_rate = {int(earth.loss_rate*100)}%  (P2/P3 อาจ drop, P1 ห้าม drop)")
    for i in range(1, 4):
        earth.send_data(lunar, f"P1 Critical Command #{i}", priority=1, label="Critical")
    for i in range(1, 4):
        earth.send_data(lunar, f"P3 Media File #{i}", priority=3, label="Media")
    time.sleep(0.3)

    # ══════════════════════════════════════════════════════
    # สถานการณ์ที่ 3: ยานเข้าจุดอับสัญญาณ (TC-02)
    # ══════════════════════════════════════════════════════
    print("\n─── [TC-02: Lunar Gateway เข้าจุดอับสัญญาณ — Offline] ───")
    lunar._is_online = False   # ตั้งตรงเพื่อไม่ให้ trigger auto-flush ก่อนเวลา
    print(f"     🔴 {lunar.name}: Offline")

    earth.send_data(lunar, "วิดีโออวยพรครอบครัว",          priority=3, label="Media")
    earth.send_data(lunar, "ผลวิเคราะห์ดิน",                priority=2, label="Scientific")
    earth.send_data(lunar, "คำสั่งหลบหลีกอุกกาบาตฉุกเฉิน!", priority=1, label="Critical")

    print(f"\n  📦 Buffer ของ Earth มี {len(earth.storage_buffer)} รายการรอส่ง")
    time.sleep(0.3)

    # ══════════════════════════════════════════════════════
    # สถานการณ์ที่ 4: สัญญาณกลับมา — ISS-02 Auto-flush (TC-03, TC-04)
    # ══════════════════════════════════════════════════════
    print("\n─── [TC-03/TC-04: สัญญาณกลับมา — ISS-02 Auto-flush + QoS ทำงาน] ───")
    lunar.is_online = True   # ← property setter จะ auto-flush ทันที

    time.sleep(0.3)

    # ══════════════════════════════════════════════════════
    # สถานการณ์ที่ 5: HITL Double-approve Guard (ISS-05)
    # ══════════════════════════════════════════════════════
    print("\n─── [ISS-05: HITL Double-approve Guard Test] ───")
    result1 = earth.hitl_approve(lunar, "Approve คำสั่งฉุกเฉิน #1")
    result2 = earth.hitl_approve(lunar, "Approve ซ้ำ #2 (ต้องถูก block)")
    print(f"     Approve #1: {'✅ สำเร็จ' if result1 else '🚫 Blocked'}")
    print(f"     Approve #2: {'✅ สำเร็จ' if result2 else '🚫 Blocked (Double-approve guard ทำงาน)'}")

    print("\n" + "=" * 60)
    print("  ✅ สิ้นสุดการจำลอง — Sprint 3 Fixes Verified")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()
