# Sprint 3 & 4
 
## Interstellar Data Mesh Simulation
 
---
 
# 1. Domain Interface Mapping และ Math Formalization (DAFT Extended Edition)
 
## 1.1 ภาพรวม
 
> Domain Interface Mapping คือกระบวนการแปลงความรู้จาก 4 สาขาวิชา (Bio / Phy / Neuro / Quantum) ให้เป็นสมการคณิตศาสตร์ที่ระบบ IDMS สามารถนำไปใช้ได้จริง โดยอ้างอิงกรอบ DAFT (Domain Agnostic Formalization Template)
 
---
 
## 1.2 Domain 1 ฟิสิกส์ (Physics)
 
> ความเชื่อมโยง: ระบบ IDMS จำลองความหน่วงของสัญญาณตามระยะทางจริงในอวกาศ และจำลองการสูญเสียสัญญาณตามกฎทางฟิสิกส์
 
**สมการความหน่วงสัญญาณ (Signal Latency)**
 
```
L = d ÷ c
```
 
- L = ความหน่วง (วินาที)
- d = ระยะทาง (เมตร)
- c = 3×10⁸ m/s
 
ตัวอย่าง: โลก--ดวงจันทร์ → L ≈ 1.28 s (one-way), RTT ≈ 2.6 s
 
**สมการการสูญเสียสัญญาณ (Path Loss)**
 
```
PL = 20·log₁₀(d) + 20·log₁₀(f) + 20·log₁₀(4π/c)
```
 
- PL = Path Loss (dB)
- f = ความถี่ (Hz)
 
การนำไปใช้: Module 2 ใช้สูตร L กำหนด `time.sleep()` จำลอง Latency เมื่อ PL เกินเกณฑ์ → สลับจาก Optical ไป RF อัตโนมัติ
 
---
 
## 1.3 Domain 2 ชีววิทยา (Biology)
 
> ความเชื่อมโยง: ข้อมูลสุขภาพนักบินอวกาศ (Bio Telemetry) ถือเป็น Priority 1 (Critical) ที่ต้องส่งถึงโลกโดยไม่ขาดหาย
 
**เกณฑ์การแจ้งเตือนสุขภาพ (Bio Alert Threshold)**
 
```
Alert = True ถ้า HR > 120 bpm หรือ HR < 40 bpm
Alert = True ถ้า SpO₂ < 90%
Alert = True ถ้า Temp > 38.5°C หรือ Temp < 35°C
```
 
**ลำดับความสำคัญข้อมูลชีวภาพ**
 
```
Priority(Bio) = 1 ถ้า Alert = True  (ส่งเป็น Critical)
Priority(Bio) = 2 ถ้า Alert = False (ส่งเป็น Scientific)
```
 
การนำไปใช้: ข้อมูล Bio ที่ Alert = True จะถูกส่งด้วย `priority=1` ระบบ QoS รับประกันว่าไม่ถูก Drop
 
---
 
## 1.4 Domain 3 ประสาทวิทยา (Neuroscience)
 
> ความเชื่อมโยง: ระบบ HITL ต้องออกแบบโดยคำนึงถึงข้อจำกัดของสมองมนุษย์ เช่น เวลาตอบสนองและความสามารถประมวลผลข้อมูล
 
**เวลาตอบสนองของมนุษย์ (Human Reaction Time)**
 
```
RT_simple  ≈ 250 ms        (การตัดสินใจง่าย)
RT_complex ≈ 500–1500 ms   (การตัดสินใจซับซ้อน)
```
 
**เกณฑ์ HITL Timeout**
 
```
T_timeout = RT_complex × Safety_Factor = 1500 × 3 = 4500 ms
```
 
ถ้าไม่มีการตอบสนองใน 4500 ms → ระบบแจ้งเตือนซ้ำ
 
การนำไปใช้: ปุ่ม Approve ใน HITL ให้เวลา ≥ 4.5 วินาที UI แสดงข้อมูลไม่เกิน 3 รายการพร้อมกัน
 
---
 
## 1.5 Domain 4 ควอนตัม (Quantum)
 
> ความเชื่อมโยง: การเข้ารหัสข้อมูล Critical ด้วยหลักการ Quantum Cryptography เพื่อความปลอดภัยสูงสุด
 
**Quantum Bit Error Rate (QBER)**
 
```
QBER = (จำนวน Bit ที่ผิดพลาด ÷ Bit ทั้งหมด) × 100%
```
 
ถ้า QBER > 11% → ช่องสัญญาณอาจถูกดักฟัง → ยกเลิกการส่ง
 
**ระดับความปลอดภัย**
 
```
Security = Critical  ถ้า QBER < 5%
Security = Warning   ถ้า 5% ≤ QBER ≤ 11%
Security = Abort     ถ้า QBER > 11% → เก็บใน Buffer รอช่องสัญญาณปลอดภัย
```
 
การนำไปใช้: ข้อมูล P1 Critical ต้องผ่านการตรวจสอบ QBER ก่อนส่งทุกครั้ง
 
---
 
## 1.6 ตารางสรุป Domain Mapping
 
| Domain      | ตัวแปรหลัก              | สมการสำคัญ              | เชื่อมกับ Module |
|-------------|------------------------|------------------------|-----------------|
| Physics     | Latency (L), Path Loss (PL) | L = d ÷ c         | Module 2        |
| Biology     | HR, SpO₂, Temp         | Alert = f(ค่าชีพจร)     | Module 1, 4     |
| Neuroscience | RT_human, T_timeout   | T_timeout = RT × 3    | HITL            |
| Quantum     | QBER, Security Level   | QBER < 11%            | Module 3        |
 
---
 
# 2. Model/Protocol Maturity และ Quality Metrics
 
## 2.1 ระดับความสมบูรณ์ของโมเดล (TRL)
 
| ระดับ TRL | คำอธิบาย                                    | สถานะ IDMS                    |
|-----------|---------------------------------------------|-------------------------------|
| TRL 1–2   | แนวคิดและหลักการเบื้องต้น                     | ผ่านแล้ว (Sprint 1)           |
| TRL 3     | หลักฐานเชิงแนวคิด (Proof of Concept)        | ผ่านแล้ว (Toy Model)          |
| TRL 4     | การตรวจสอบในสภาพแวดล้อมจำลอง               | ผ่านแล้ว (pytest TC-01~05)   |
| TRL 5–6   | การทดสอบในสภาพแวดล้อมที่เกี่ยวข้อง           | Sprint 3 & 4                  |
 
---
 
## 2.2 ความสมบูรณ์ของโปรโตคอล
 
| โปรโตคอล                    | มาตรฐานอ้างอิง        | สถานะ               |
|-----------------------------|-----------------------|---------------------|
| DTN Bundle Protocol         | RFC 9171 (CCSDS)      | จำลองครบ            |
| QoS Priority Queue          | ITU-T Y.1291          | ผ่าน TC-04          |
| Store-and-Forward           | RFC 5050              | ผ่าน TC-02, TC-03   |
| Hybrid Failover (Optical→RF) | NASA O2O Standard    | จำลองบางส่วน        |
 
---
 
## 2.3 ตัวชี้วัดคุณภาพ (Quality Metrics)
 
| ตัวชี้วัด           | สูตร                  | เป้าหมาย | ผลจริง | สถานะ |
|--------------------|-----------------------|---------|--------|-------|
| PLR – P1 Critical  | (Drop÷Sent)×100%      | 0%      | 0%     | PASS  |
| PLR – P3 Media     | (Drop÷Sent)×100%      | ≤ 90%   | ~90%   | PASS  |
| Recovery Time      | T_empty − T_online    | < 5s    | ~2s    | PASS  |
| Buffer Residual    | Items_left÷Total      | 0%      | 0%     | PASS  |
| QoS Order Accuracy | Correct÷Total×100%    | 100%    | 100%   | PASS  |
 
---
 
# 3. จริยธรรมและข้อบังคับ (Ethics & Regulations)
 
## 3.1 หลักจริยธรรม 4 ด้าน
 
**ความปลอดภัยของชีวิต (Human Safety First)**
- ข้อมูล Priority 1 ต้องถูกส่งก่อนเสมอ ไม่อนุญาตให้ Drop แม้วิกฤต
- Safety_Score = 1 − PLR(Critical) → ต้องได้ 1.0 เสมอ
 
**ความโปร่งใส (Transparency)**
- ระบบต้องแสดงสถานะ Buffer, QoS และ Routing Decision ให้ตรวจสอบได้ตลอดเวลา
 
**ความเป็นส่วนตัว (Data Privacy)**
- ข้อมูลส่วนตัว (P3/Media) ต้องไม่ถูกนำไปใช้โดยไม่ได้รับอนุญาต
 
**ความยุติธรรม (Fairness)**
- เกณฑ์ Priority ใช้ประเภทข้อมูลเป็นเกณฑ์ ไม่ใช่ตัวตนของผู้ส่ง
 
---
 
## 3.2 ข้อบังคับที่เกี่ยวข้อง
 
| ข้อบังคับ                         | ความเกี่ยวข้อง                             |
|----------------------------------|-------------------------------------------|
| ITU Radio Regulations            | การใช้คลื่นความถี่ในอวกาศ                  |
| CCSDS Bundle Protocol (RFC 9171) | มาตรฐาน DTN สากล                         |
| NASA O2O Communication Standard  | Optical Link สำหรับภารกิจ Artemis         |
| GDPR                             | การปกป้องข้อมูลส่วนบุคคล                  |
 
---
 
# 4. Governance และ Human-in-the-Loop (HITL)
 
## 4.1 โครงสร้าง Governance
 
**ระดับที่ 1 – ระบบอัตโนมัติ (Algorithm)**
- จัดการข้อมูล P2/P3, Store-and-Forward และ QoS Flush โดยอัตโนมัติ
 
**ระดับที่ 2 – Human-in-the-Loop**
- ต้องอนุมัติก่อนส่งข้อมูล P1 Critical ทุกครั้ง
- สามารถ Override Priority ได้ด้วยตนเอง
 
**ระดับที่ 3 – Mission Commander**
- ตัดสินใจในกรณีฉุกเฉินสูงสุด และ Shutdown ระบบได้ทันที
 
---
 
## 4.2 กฎของ HITL
 
| สถานการณ์                          | ระบบอัตโนมัติ | ต้องการ HITL |
|-----------------------------------|:-------------:|:------------:|
| ส่งข้อมูล P2/P3 ปกติ               | ✓             |              |
| ส่งข้อมูล P1 Critical              |               | ✓            |
| Store-and-Forward เมื่อ Offline   | ✓             |              |
| QoS Flush หลัง Recovery           | ✓             |              |
| Override Priority                  |               | ✓            |
 
---
 
## 4.3 สมการ HITL Effectiveness
 
```
HITL_Effectiveness = (จำนวนครั้งที่มนุษย์แก้ไขการตัดสินใจผิด)
                   ÷ (จำนวนครั้งที่ระบบตัดสินใจผิด) × 100%
```
 
เป้าหมาย: HITL_Effectiveness ≥ 95%
 
---
 
## 4.4 การใช้งาน HITL ใน dtn_v2.html
 
- เปิดแท็บ HITL ในหน้าเว็บ `dtn_v2.html`
- เมื่อมีข้อมูล P1 Critical รอส่ง ระบบจะหยุดรอการอนุมัติ
- กดปุ่ม **"Approve"** ภายใน 4,500 ms เพื่ออนุมัติ
- ถ้าไม่มีการตอบสนอง → ระบบแจ้งเตือนซ้ำและบันทึก Log
 
---
 
# 5. สรุปภาพรวม Sprint 3 & 4
 
| หัวข้อ                        | งานที่ทำ                          | สถานะ          |
|------------------------------|----------------------------------|----------------|
| Domain Mapping (Physics)     | สูตร Latency และ Path Loss        | เสร็จ          |
| Domain Mapping (Biology)     | เกณฑ์ Bio Alert และ Priority      | เสร็จ          |
| Domain Mapping (Neuroscience) | สูตร HITL Timeout               | เสร็จ          |
| Domain Mapping (Quantum)     | สูตร QBER และ Security Level     | เสร็จ          |
| Model Maturity (TRL)         | ประเมินระดับ TRL 4                | เสร็จ          |
| Quality Metrics              | ผ่านครบ 5 ตัวชี้วัด               | PASS ทั้งหมด   |
| Ethics                       | อธิบาย 4 มิติจริยธรรม             | เสร็จ          |
| Governance & HITL            | กฎ HITL และโครงสร้าง 3 ระดับ     | เสร็จ          |
