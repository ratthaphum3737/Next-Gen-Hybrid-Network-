# แบบจำลองระบบ (Toy Model) — Python Source Code

จำลองการทำงานของ DTN (Delay/Disruption Tolerant Networking) พร้อมระบบ QoS (Quality of Service)

```python
import time
 
class SpaceNode:
    def __init__(self, name):
        self.name = name
        self.is_online = True  # True = ปกติ, False = สัญญาณขาด
        self.storage_buffer = []  # Buffer สำหรับ Store-and-Forward
 
    def receive_data(self, data, label):
        print(f'[{self.name}] รับข้อมูลแล้ว: [{label}] "{data}"')
 
    def send_data(self, destination, data, priority=3, label='ทั่วไป'):
        print(f'[{self.name}] ส่งข้อมูล [{label}] (Priority:{priority}) -> "{data}"')
        if destination.is_online:
            print('   -> Link: ปกติ (Forward ทันที)')
            destination.receive_data(data, label)
        else:
            print('   -> Link: ล้มเหลว! -> DTN: Store ลง Buffer')
            self.storage_buffer.append((priority, time.time(), destination, data, label))
 
    def process_buffer(self):
        if not self.storage_buffer:
            return
        print(f'[{self.name}] เปิดระบบ QoS จัดเรียงคิว...')
        # QoS: จัดเรียงตาม Priority (น้อย = สำคัญมาก) แล้วตามเวลา (FIFO)
        self.storage_buffer.sort(key=lambda x: (x[0], x[1]))
        pending = self.storage_buffer.copy()
        self.storage_buffer = []
        for priority, ts, dest, data, label in pending:
            if dest.is_online:
                print(f'   -> QoS Forward (P{priority}): "{data}"')
                dest.receive_data(data, label)
                time.sleep(0.5)
            else:
                self.storage_buffer.append((priority, ts, dest, data, label))
 
# ─── เริ่มการจำลองสถานการณ์ ───────────────────────────────────────
print('=== จำลอง Interstellar Data Mesh (DTN + QoS) ===')
earth  = SpaceNode('Earth Mission Control')
lunar  = SpaceNode('Lunar Gateway')
 
# สถานการณ์ที่ 1: สัญญาณปกติ
print('--- [สถ.1: สัญญาณชัดเจน] ---')
earth.send_data(lunar, 'ตรวจสอบระบบนำทาง', priority=1, label='Critical')
time.sleep(1)
 
# สถานการณ์ที่ 2: สัญญาณขาดหาย
print('--- [สถ.2: ยานเข้าจุดอับสัญญาณ] ---')
lunar.is_online = False
earth.send_data(lunar, 'วิดีโออวยพรครอบครัว', priority=3, label='Media')
earth.send_data(lunar, 'ภาพถ่ายพื้นผิวดวงจันทร์', priority=2, label='Scientific')
earth.send_data(lunar, 'คำสั่งหลบหลีกอุกกาบาตฉุกเฉิน!', priority=1, label='Critical')
time.sleep(1)
 
# สถานการณ์ที่ 3: สัญญาณกลับมา QoS ทำงาน
print('--- [สถ.3: สัญญาณกลับมา ระบบ DTN+QoS เริ่มทำงาน] ---')
lunar.is_online = True
earth.process_buffer()
print('=== สิ้นสุดการจำลอง ===')