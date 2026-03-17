"""
space_node.py
=============
Module 1: Network Node Environment  — สร้าง Class ของโหนดอวกาศแต่ละตัว
Module 3: DTN Store-and-Forward Logic — เก็บข้อมูลเมื่อสัญญาณขาด แล้วส่งต่อเมื่อกลับมา
Module 4: QoS & Traffic Management   — จัดลำดับความสำคัญในการส่งข้อมูล

Sprint Beta — Sprint 3 Fixes:
  ISS-01: Packet Loss Logic — P1 Critical ต้องไม่ถูก drop เด็ดขาด
  ISS-02: Auto-flush Buffer — process_buffer() อัตโนมัติเมื่อโหนดปลายทาง False → True
          ใช้ Subscriber Pattern: destination track pending senders ไว้ใน _pending_senders
  ISS-03: FIFO Tie-breaking — sort key (priority, timestamp) ✅ (ยืนยันแล้ว)
  ISS-05: HITL Double-approve Guard — _hitl_pending flag ป้องกัน race condition
"""

import time
import random


class SpaceNode:
    """
    แทนโหนดอวกาศ 1 ตัว เช่น Earth Mission Control หรือ Lunar Gateway

    Attributes:
      is_online         : สถานะว่าออนไลน์อยู่หรือเปล่า (property — ISS-02 auto-flush)
      storage_buffer    : คิวเก็บข้อมูลเมื่อปลายทางออฟไลน์ (Store-and-Forward)
      loss_rate         : อัตรา Packet Loss (0.0–1.0) ของ link ขาออก (ISS-01)
      _pending_senders  : set ของ SpaceNode ที่มี buffer ค้างส่งหาโหนดนี้ (ISS-02)
      _hitl_pending     : flag ป้องกัน HITL double-approve (ISS-05)

    priority levels:
      1 = Critical   (คำสั่งฉุกเฉิน, Telemetry) — ห้าม drop เด็ดขาด
      2 = Scientific (ภาพถ่าย, ข้อมูลวิทยาศาสตร์)
      3 = Media      (วิดีโอ, ไฟล์ทั่วไป)
    """

    def __init__(self, name: str, loss_rate: float = 0.0):
        self.name = name
        self._is_online = True
        self.storage_buffer = []        # [(priority, timestamp, destination, data, label), ...]
        self.loss_rate = loss_rate      # ISS-01: อัตรา Packet Loss ของ link ขาออก
        self._pending_senders = set()   # ISS-02: senders ที่มี buffer ค้างส่งหาโหนดนี้
        self._hitl_pending = False      # ISS-05: HITL double-approve guard

    # ------------------------------------------------------------------
    # ISS-02: Property is_online
    # เมื่อโหนดกลับมา Online → แจ้ง pending_senders ทุกตัวให้ flush buffer
    # ------------------------------------------------------------------
    @property
    def is_online(self) -> bool:
        return self._is_online

    @is_online.setter
    def is_online(self, value: bool) -> None:
        was_offline = not self._is_online
        self._is_online = value

        if value and was_offline:
            # ISS-02: แจ้งทุก sender ที่มี buffer ค้างส่งหาโหนดนี้ให้ flush ทันที
            senders_to_notify = list(self._pending_senders)
            if senders_to_notify:
                print(f"\n  🔔 [{self.name}] กลับมา Online → Auto-flush Buffer จาก {len(senders_to_notify)} sender(s)")
                for sender in senders_to_notify:
                    sender.process_buffer()

    # ------------------------------------------------------------------
    # รับข้อมูล
    # ------------------------------------------------------------------
    def receive_data(self, data: str, label: str) -> None:
        """แสดงผลเมื่อโหนดนี้ได้รับข้อมูลสำเร็จ"""
        print(f"  ✅ [{self.name}] รับข้อมูลแล้ว: [{label}] \"{data}\"")

    # ------------------------------------------------------------------
    # ISS-01: ส่งข้อมูล + Packet Loss Logic
    # ------------------------------------------------------------------
    def send_data(
        self,
        destination: "SpaceNode",
        data: str,
        priority: int = 3,
        label: str = "ทั่วไป",
    ) -> None:
        """
        ส่งข้อมูลไปยังโหนดปลายทาง
        - ถ้าปลายทาง Online  → ตรวจ Packet Loss (P1 Critical bypass drop เสมอ)
        - ถ้าปลายทาง Offline → Store ลง Buffer + register ตัวเองใน destination._pending_senders

        ISS-01 Fix: P1 Critical ข้าม drop logic ทุกกรณี
        ISS-02 Fix: register self ใน destination._pending_senders เพื่อรอ auto-flush
        """
        print(f"\n  📤 [{self.name}] ส่งข้อมูล [{label}] (Priority:{priority}) → \"{data}\"")

        if destination.is_online:
            # ISS-01: P1 Critical — Bypass Drop เสมอ
            if priority == 1:
                print("     Link: ปกติ → P1 Critical: Bypass Drop → Forward ทันที")
                destination.receive_data(data, label)
            elif self.loss_rate > 0 and random.random() < self.loss_rate:
                print(f"     ⚡ Packet Loss! ({int(self.loss_rate*100)}%) → [{label}] \"{data}\" ถูก Drop")
            else:
                print("     Link: ปกติ → Forward ทันที")
                destination.receive_data(data, label)
        else:
            # ISS-02: Store + register เป็น pending_sender ของ destination
            print("     Link: ล้มเหลว! → DTN: Store ลง Buffer")
            self.storage_buffer.append(
                (priority, time.time(), destination, data, label)
            )
            destination._pending_senders.add(self)  # ISS-02: subscriber registration

    # ------------------------------------------------------------------
    # ISS-05: HITL approve guard — ป้องกัน double-approve
    # ------------------------------------------------------------------
    def hitl_approve(
        self,
        destination: "SpaceNode",
        data: str,
        label: str = "Critical",
    ) -> bool:
        """
        ISS-05: Human-in-the-Loop approve สำหรับ P1 Critical
        ใช้ _hitl_pending flag ป้องกัน race condition / double-approve

        Returns:
          True  — อนุมัติสำเร็จ ส่งข้อมูลทันที
          False — มี approve ค้างอยู่ (double-approve blocked)
        """
        if self._hitl_pending:
            print(f"  🚫 [{self.name}] HITL: Double-approve blocked! มี request ค้างอยู่แล้ว")
            return False

        self._hitl_pending = True
        print(f"  🔐 [{self.name}] HITL: รอ Human Operator อนุมัติ P1 → \"{data}\"")
        print(f"  ✅ [{self.name}] HITL: Approved → ส่ง P1 \"{data}\" → [{destination.name}]")
        self._hitl_pending = False      # reset flag หลัง approve เสร็จ
        destination.receive_data(data, label)
        return True

    # ------------------------------------------------------------------
    # ISS-03: ประมวลผล Buffer (QoS + FIFO Tie-breaking)
    # ------------------------------------------------------------------
    def process_buffer(self) -> None:
        """
        เมื่อเรียกฟังก์ชันนี้ ระบบจะ:
        1. เรียงข้อมูลใน Buffer ตาม Priority (น้อย = สำคัญมาก) แบบ FIFO
           ISS-03: key=lambda x: (x[0], x[1]) → x[0]=priority, x[1]=timestamp
        2. ส่งข้อมูลที่ปลายทางกลับมา Online แล้ว
        3. เก็บข้อมูลที่ปลายทางยังออฟไลน์อยู่ไว้ใน Buffer ต่อไป
        """
        if not self.storage_buffer:
            print(f"\n  [{self.name}] Buffer ว่างเปล่า ไม่มีอะไรต้องส่ง")
            return

        print(f"\n  🔄 [{self.name}] เปิดระบบ QoS จัดเรียงคิว ({len(self.storage_buffer)} รายการ)...")

        # ISS-03: QoS + FIFO Tie-breaking
        self.storage_buffer.sort(key=lambda x: (x[0], x[1]))

        pending = self.storage_buffer.copy()
        self.storage_buffer = []

        for priority, ts, dest, data, label in pending:
            if dest.is_online:
                print(f"     QoS Forward (P{priority}/{label}): \"{data}\"")
                dest.receive_data(data, label)
                dest._pending_senders.discard(self)  # unregister เมื่อส่งสำเร็จ
                time.sleep(0.1)
            else:
                print(f"     ⏳ ปลายทางยังออฟไลน์ เก็บ (P{priority}/{label}) ไว้ก่อน")
                self.storage_buffer.append((priority, ts, dest, data, label))

        # ถ้า buffer ว่างแล้ว ให้ unregister ออกจาก destinations ทั้งหมด
        if not self.storage_buffer:
            for _, _, dest, _, _ in pending:
                dest._pending_senders.discard(self)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        status = "🟢 Online" if self.is_online else "🔴 Offline"
        return f"SpaceNode('{self.name}', {status}, buffer={len(self.storage_buffer)})"
