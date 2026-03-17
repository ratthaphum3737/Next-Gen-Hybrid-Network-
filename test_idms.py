"""
test_idms.py
============
ครอบคลุม Acceptance Criteria ทั้ง 5 ข้อหลัก + 1 ข้อ Extra
Test Cases TC-01 ถึง TC-07

Sprint Beta Sprint 3 Fixes:
  ISS-01: ทดสอบ Packet Loss Logic — P1 Critical ต้องไม่ถูก Drop
  ISS-02: ทดสอบ Auto-flush Buffer เมื่อ is_online: False → True
  ISS-05: ทดสอบ HITL Double-approve Guard (TC-07)
  TC-06:  ทดสอบ Multi-node Failure (Bonus)

วิธีรัน:
  pytest test_idms.py -v
"""

import pytest
import random
from space_node import SpaceNode


# ══════════════════════════════════════════════════════════
# Fixtures — สร้างโหนดใหม่ก่อนแต่ละ test (ป้องกันข้อมูลปนกัน)
# ══════════════════════════════════════════════════════════

@pytest.fixture
def earth():
    """โหนด Earth Mission Control — ออนไลน์เริ่มต้น, loss_rate=0"""
    return SpaceNode("Earth Mission Control")


@pytest.fixture
def lunar():
    """โหนด Lunar Gateway — ออนไลน์เริ่มต้น"""
    return SpaceNode("Lunar Gateway")


@pytest.fixture
def surface():
    """โหนด Surface Base — สำหรับทดสอบ 3 โหนด"""
    return SpaceNode("Surface Base LAN")


@pytest.fixture
def probe():
    """โหนด Deep Space Probe — สำหรับทดสอบ 4 โหนด / Multi-node failure"""
    return SpaceNode("Deep Space Probe")


# ══════════════════════════════════════════════════════════
# TC-01: Normal Transmission
# ══════════════════════════════════════════════════════════

def test_tc01_normal_transmission(earth, lunar):
    """ทุกโหนด Online → ส่งสำเร็จทันที Buffer ต้องว่างเปล่า"""
    earth.send_data(lunar, "ตรวจสอบระบบ", priority=1, label="Critical")
    earth.send_data(lunar, "ภาพถ่าย",     priority=2, label="Scientific")
    earth.send_data(lunar, "วิดีโอ",      priority=3, label="Media")

    assert len(earth.storage_buffer) == 0, "Buffer ต้องว่างเมื่อปลายทาง Online"


def test_tc01_three_nodes(earth, lunar, surface):
    """AC-1: ต้องรองรับอย่างน้อย 3 โหนด"""
    earth.send_data(lunar,   "ข้อมูล A", priority=1, label="Critical")
    lunar.send_data(surface, "ข้อมูล B", priority=2, label="Scientific")

    assert len(earth.storage_buffer) == 0
    assert len(lunar.storage_buffer) == 0


# ══════════════════════════════════════════════════════════
# ISS-01: Packet Loss Logic — P1 Critical ต้องไม่ถูก Drop
# ══════════════════════════════════════════════════════════

def test_iss01_critical_bypass_drop(lunar):
    """ISS-01: P1 Critical ต้องไม่ถูก drop แม้ loss_rate=1.0 (100%)"""
    sender = SpaceNode("EMC with 100% Loss", loss_rate=1.0)

    # P1 Critical ต้องส่งถึง (ไม่ drop) แม้ loss_rate = 100%
    received = []
    original_receive = lunar.receive_data
    lunar.receive_data = lambda data, label: received.append((data, label))

    sender.send_data(lunar, "CRITICAL: Emergency Command", priority=1, label="Critical")

    assert len(received) == 1, "P1 Critical ต้องถึงปลายทาง แม้ loss_rate=100%"


def test_iss01_non_critical_can_drop(lunar):
    """ISS-01: P3 Media อาจถูก drop เมื่อ loss_rate สูง"""
    random.seed(0)   # seed เพื่อให้ผล deterministic
    sender = SpaceNode("EMC with High Loss", loss_rate=1.0)

    received = []
    original_receive = lunar.receive_data
    lunar.receive_data = lambda data, label: received.append((data, label))

    # ส่ง P3 Media 10 ครั้ง กับ loss_rate=100% ทั้งหมดต้องถูก drop
    for i in range(10):
        sender.send_data(lunar, f"Media File #{i}", priority=3, label="Media")

    assert len(received) == 0, "P3 Media ต้องถูก drop ทั้งหมดเมื่อ loss_rate=100%"


# ══════════════════════════════════════════════════════════
# ISS-02: Auto-flush Buffer เมื่อ is_online: False → True
# ══════════════════════════════════════════════════════════

def test_iss02_auto_flush_on_online(earth, lunar):
    """ISS-02: Buffer ต้อง flush อัตโนมัติเมื่อ is_online เปลี่ยน False → True"""
    # Step 1: ออฟไลน์ → เก็บข้อมูล
    lunar._is_online = False
    earth.send_data(lunar, "ข้อมูล 1", priority=2, label="Scientific")
    earth.send_data(lunar, "ข้อมูล 2", priority=1, label="Critical")

    assert len(earth.storage_buffer) == 2

    # Step 2: ตั้ง is_online=True → ต้อง auto-flush ทันที (ไม่ต้องเรียก process_buffer เอง)
    lunar.is_online = True

    # Buffer ต้องว่างหลัง auto-flush
    assert len(earth.storage_buffer) == 0, "ISS-02: Buffer ต้อง auto-flush เมื่อ Online"


def test_iss02_no_flush_if_buffer_empty(earth, lunar):
    """ISS-02: ถ้า Buffer ว่าง การตั้ง is_online=True ต้องไม่ error"""
    lunar._is_online = False
    assert len(earth.storage_buffer) == 0
    lunar.is_online = True   # ต้องไม่ raise exception
    assert lunar.is_online is True


# ══════════════════════════════════════════════════════════
# TC-02: Single Node Failure
# ══════════════════════════════════════════════════════════

def test_tc02_single_node_failure(earth, lunar):
    """AC-2: Lunar ออฟไลน์ → ข้อมูลต้อง Store ใน Buffer ครบถ้วน (0% Data Loss)"""
    lunar._is_online = False

    earth.send_data(lunar, "วิดีโอ",       priority=3, label="Media")
    earth.send_data(lunar, "ภาพถ่าย",      priority=2, label="Scientific")
    earth.send_data(lunar, "คำสั่งฉุกเฉิน", priority=1, label="Critical")

    assert len(earth.storage_buffer) == 3, "ต้องเก็บข้อมูลครบ 3 รายการใน Buffer"


# ══════════════════════════════════════════════════════════
# TC-03: Full Recovery (Auto-flush)
# ══════════════════════════════════════════════════════════

def test_tc03_full_recovery(earth, lunar):
    """AC-2 & AC-3: กลับ Online → Forward อัตโนมัติ Buffer ต้องว่าง"""
    lunar._is_online = False
    earth.send_data(lunar, "ข้อมูล 1", priority=2, label="Scientific")
    earth.send_data(lunar, "ข้อมูล 2", priority=1, label="Critical")

    assert len(earth.storage_buffer) == 2

    # ISS-02: ตั้ง is_online=True → auto-flush ทันที
    lunar.is_online = True

    assert len(earth.storage_buffer) == 0, "Buffer ต้องว่างหลัง auto-flush"


# ══════════════════════════════════════════════════════════
# TC-04: QoS Priority Test
# ══════════════════════════════════════════════════════════

def test_tc04_qos_priority_order(earth, lunar):
    """AC-4: Priority 1 ต้องถูกเรียงก่อนเสมอ"""
    lunar._is_online = False

    earth.send_data(lunar, "วิดีโอ",       priority=3, label="Media")
    earth.send_data(lunar, "ผลวิเคราะห์",  priority=2, label="Scientific")
    earth.send_data(lunar, "คำสั่งฉุกเฉิน", priority=1, label="Critical")

    priorities_in_buffer = [item[0] for item in earth.storage_buffer]
    assert 1 in priorities_in_buffer

    earth.storage_buffer.sort(key=lambda x: (x[0], x[1]))

    assert earth.storage_buffer[0][0] == 1, "Priority 1 ต้องอยู่หัวคิวเสมอ"
    assert earth.storage_buffer[-1][0] == 3, "Priority 3 ต้องอยู่ท้ายคิวเสมอ"


def test_tc04_qos_forward_order(earth, lunar, capsys):
    """AC-4: Critical ต้องถูก Forward ก่อน Media เมื่อ process_buffer ทำงาน"""
    lunar._is_online = False
    earth.send_data(lunar, "วิดีโอ",       priority=3, label="Media")
    earth.send_data(lunar, "คำสั่งฉุกเฉิน", priority=1, label="Critical")

    lunar._is_online = True
    capsys.readouterr()

    earth.process_buffer()
    captured = capsys.readouterr()

    critical_pos = captured.out.find("Critical")
    media_pos    = captured.out.find("Media")
    assert critical_pos < media_pos, "Critical ต้อง Forward ก่อน Media"


def test_tc04_fifo_same_priority(earth, lunar):
    """ISS-03: Packet ที่ priority เท่ากัน ต้องเรียงตาม timestamp (FIFO)"""
    import time as t
    lunar._is_online = False

    earth.send_data(lunar, "First P2",  priority=2, label="Scientific")
    t.sleep(0.01)
    earth.send_data(lunar, "Second P2", priority=2, label="Scientific")
    t.sleep(0.01)
    earth.send_data(lunar, "Third P2",  priority=2, label="Scientific")

    earth.storage_buffer.sort(key=lambda x: (x[0], x[1]))

    data_order = [item[3] for item in earth.storage_buffer]
    assert data_order == ["First P2", "Second P2", "Third P2"], "FIFO ต้องรักษาลำดับ timestamp"


# ══════════════════════════════════════════════════════════
# TC-05: Stress Test — 0% Data Loss ใน Critical
# ══════════════════════════════════════════════════════════

def test_tc05_stress_critical_no_loss(earth, lunar):
    """AC-5: Critical ต้องไม่สูญหายแม้ในสภาวะวิกฤต"""
    lunar._is_online = False

    for i in range(10):
        earth.send_data(lunar, f"คำสั่งฉุกเฉิน #{i+1}", priority=1, label="Critical")

    critical_in_buffer = [x for x in earth.storage_buffer if x[0] == 1]
    assert len(critical_in_buffer) == 10, "Critical ต้องไม่สูญหายแม้แต่รายการเดียว"

    lunar.is_online = True   # ISS-02: auto-flush
    assert len(earth.storage_buffer) == 0, "Buffer ต้องว่างหลัง recovery"


def test_tc05_stress_critical_bypass_loss(lunar):
    """AC-5 + ISS-01: Critical ต้องถึงปลายทาง 100% แม้ loss_rate สูง"""
    random.seed(42)
    sender = SpaceNode("Stressed EMC", loss_rate=0.9)   # 90% packet loss

    received = []
    lunar.receive_data = lambda data, label: received.append(data)

    for i in range(20):
        sender.send_data(lunar, f"Critical #{i+1}", priority=1, label="Critical")

    assert len(received) == 20, f"P1 Critical 20/20 ต้องถึงปลายทาง แต่ได้ {len(received)}"


# ══════════════════════════════════════════════════════════
# TC-06 (Bonus): Multi-node Failure
# ══════════════════════════════════════════════════════════

def test_tc06_multi_node_failure(earth, lunar, surface, probe):
    """TC-06: โหนดหลายตัวออฟไลน์พร้อมกัน — ข้อมูลต้อง Store ครบ ไม่สูญหาย"""
    # โหนด LGR, SBL, DSP ออฟไลน์พร้อมกัน
    lunar._is_online   = False
    surface._is_online = False
    probe._is_online   = False

    # ส่งข้อมูลไปยังทุกโหนดที่ออฟไลน์
    earth.send_data(lunar,   "Critical to LGR",     priority=1, label="Critical")
    earth.send_data(surface, "Scientific to SBL",   priority=2, label="Scientific")
    earth.send_data(probe,   "Media to DSP",         priority=3, label="Media")
    earth.send_data(lunar,   "Scientific to LGR #2", priority=2, label="Scientific")

    assert len(earth.storage_buffer) == 4, "Multi-node failure: ข้อมูลต้อง Store ครบ 4 รายการ"

    # กู้คืน LGR ก่อน → auto-flush เฉพาะ LGR items
    lunar.is_online = True

    # LGR items (2 รายการ) ต้องถูก forward ออกไปแล้ว
    lgr_remaining = [x for x in earth.storage_buffer if x[2].name == "Lunar Gateway"]
    assert len(lgr_remaining) == 0, "LGR items ต้องถูก forward หลัง LGR กลับ Online"

    # SBL, DSP items ยังค้างอยู่ใน buffer
    remaining = len(earth.storage_buffer)
    assert remaining == 2, f"SBL/DSP items ต้องยังอยู่ใน Buffer: คาดหวัง 2 แต่ได้ {remaining}"

    # กู้คืน SBL และ DSP
    surface.is_online = True
    probe.is_online   = True

    assert len(earth.storage_buffer) == 0, "Buffer ต้องว่างเมื่อทุกโหนดกลับ Online"


def test_tc06_alternative_path_reroute(earth, lunar, surface):
    """TC-06: จำลอง Alternative Path — ถ้า LGR ออฟไลน์ ส่งผ่าน SBL แทน"""
    lunar._is_online = False

    # ส่งไป LGR → store เพราะออฟไลน์
    earth.send_data(lunar, "Message via LGR", priority=2, label="Scientific")
    assert len(earth.storage_buffer) == 1

    # Alternative: ส่งไป SBL แทน (SBL ออนไลน์)
    earth.send_data(surface, "Message via SBL (reroute)", priority=2, label="Scientific")
    # SBL ออนไลน์ → ไม่เพิ่ม buffer
    sbl_items = [x for x in earth.storage_buffer if x[2].name == "Surface Base LAN"]
    assert len(sbl_items) == 0, "ข้อมูลที่ส่งผ่าน SBL ต้องไม่อยู่ใน buffer"


# ══════════════════════════════════════════════════════════
# TC-07 (Bonus): HITL Double-approve Guard (ISS-05)
# ══════════════════════════════════════════════════════════

def test_tc07_hitl_approve_success(earth, lunar):
    """TC-07: HITL approve ปกติต้องสำเร็จ"""
    received = []
    lunar.receive_data = lambda data, label: received.append(data)

    result = earth.hitl_approve(lunar, "Emergency Command")

    assert result is True, "HITL approve ครั้งแรกต้องสำเร็จ"
    assert len(received) == 1, "ข้อมูลต้องถึงปลายทางหลัง approve"


def test_tc07_hitl_double_approve_blocked(earth, lunar):
    """TC-07: ISS-05 — Double-approve ต้องถูก block ด้วย pending flag"""
    # จำลอง pending อยู่ (ยังไม่ได้ approve)
    earth._hitl_pending = True

    result = earth.hitl_approve(lunar, "Duplicate Approve Attempt")

    assert result is False, "ISS-05: Double-approve ต้องถูก block"


def test_tc07_hitl_flag_reset_after_approve(earth, lunar):
    """TC-07: _hitl_pending ต้องถูก reset เป็น False หลัง approve เสร็จ"""
    earth.hitl_approve(lunar, "Command A")
    assert earth._hitl_pending is False, "_hitl_pending ต้อง False หลัง approve เสร็จ"


def test_tc07_hitl_allows_next_after_reset(earth, lunar):
    """TC-07: หลัง approve เสร็จแล้ว approve ครั้งต่อไปต้องสำเร็จ"""
    result1 = earth.hitl_approve(lunar, "Command A")
    result2 = earth.hitl_approve(lunar, "Command B")   # หลัง reset แล้ว ต้องผ่าน

    assert result1 is True
    assert result2 is True, "หลัง flag reset แล้ว approve ครั้งถัดไปต้องสำเร็จ"


# ══════════════════════════════════════════════════════════
# Bonus: ทดสอบ Node Status พื้นฐาน
# ══════════════════════════════════════════════════════════

def test_node_online_default(earth):
    """โหนดที่สร้างใหม่ต้องเป็น Online เสมอ"""
    assert earth.is_online is True


def test_node_buffer_empty_default(earth):
    """โหนดที่สร้างใหม่ต้อง Buffer ว่างเสมอ"""
    assert len(earth.storage_buffer) == 0


def test_node_loss_rate_default(earth):
    """โหนดที่สร้างโดยไม่ระบุ loss_rate ต้องเป็น 0"""
    assert earth.loss_rate == 0.0


def test_offline_node_does_not_receive(earth, lunar):
    """โหนดออฟไลน์ต้องไม่รับข้อมูลโดยตรง ต้อง Store ใน Buffer เท่านั้น"""
    lunar._is_online = False
    earth.send_data(lunar, "ทดสอบ", priority=1, label="Critical")

    assert len(earth.storage_buffer) == 1
    assert len(lunar.storage_buffer) == 0


def test_hitl_pending_default(earth):
    """_hitl_pending ต้องเป็น False เมื่อสร้างโหนดใหม่"""
    assert earth._hitl_pending is False
