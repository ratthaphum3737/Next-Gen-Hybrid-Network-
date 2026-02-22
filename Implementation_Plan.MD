# แผนการดำเนินงานและพัฒนาระบบ (Implementation Plan)

## 2.1 เครื่องมือและเทคโนโลยีที่ใช้ (Technology Stack)

| เครื่องมือ / เทคโนโลยี | วัตถุประสงค์การใช้งาน |
|----------------------|----------------------|
| Python 3.x (ภาษาหลัก) | ความยืดหยุ่นสูง รองรับ Network Simulation Library ครบถ้วน |
| asyncio (Library) | จัดการ Concurrency จำลองโหนดหลายตัวทำงานพร้อมกัน |
| NetworkX (Library) | สร้างกราฟโครงสร้างเครือข่ายแบบ Mesh Topology |
| pytest (Framework) | Unit Testing และ Integration Testing ทุก Module |
| Git + GitHub Actions | Version Control และระบบ CI/CD อัตโนมัติ |
| Wireshark (Tool) | วิเคราะห์ Packet และตรวจสอบประสิทธิภาพเครือข่าย |

## 2.2 โครงสร้างโมดูลซอฟต์แวร์ (Software Module Breakdown)
การพัฒนาซอฟต์แวร์จำลองแบ่งออกเป็น 4 โมดูลหลัก

### Module 1 — Network Node Environment
- สร้าง Class พื้นฐานสำหรับ Node ที่เป็นตัวแทนของ Earth Mission Control, Lunar Gateway, Surface Base และ Deep Space Probe
- พัฒนาระบบ State Machine เพื่อตรวจสอบสถานะว่าโหนดนั้น Online หรือ Offline/Disrupted

### Module 2 — Link Delay & Disruption Engine
- เขียนฟังก์ชันจำลองความหน่วงของสัญญาณ (Latency Simulator) โดยอิงตามระยะทางในอวกาศ เช่น RTT โลก–ดวงจันทร์ ≈ 2.6 วินาที
- พัฒนากลไกสุ่ม Packet Loss และจำลองสัญญาณขาดหายชั่วคราว (Transient Disruption) เพื่อทดสอบความทนทาน

### Module 3 — DTN Store-and-Forward Logic
- พัฒนาระบบ Bundle Manager ในแต่ละโหนดเพื่อทำหน้าที่เก็บ Bundle ใน Persistent Storage Buffer
- เขียนลอจิก Link Assessment หากโหนดปลายทางไม่พร้อม ระบบจะกักเก็บข้อมูลและส่งต่ออัตโนมัติเมื่อเส้นทางฟื้นคืน

### Module 4 — QoS & Traffic Management
- ประยุกต์ใช้โครงสร้างข้อมูลแบบ Priority Queue สำหรับจัดลำดับการส่งข้อมูล
- เขียนฟังก์ชันคัดกรองประเภท Packet (Critical / Scientific / Media) และเรียงลำดับการส่งออกตาม Priority