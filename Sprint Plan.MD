# แผนการทำงาน Sprint และบทบาทของทีม

## 4.1 แผนการดำเนินงาน 4 สัปดาห์ (Sprint Alpha – 1)

| สัปดาห์ | เป้าหมายหลัก (Milestone) | งานรายละเอียด |
|--------|---------------------------|---------------|
| Week 1 | Foundation & Environment | DevOps ตั้งค่า GitHub Repository, กำหนด Branching Strategy / Engineer พัฒนาโครงสร้าง Class Module 1 / Architect + Specialist ตรวจสอบ Logic ให้ตรงกับ Architecture Spec |
| Week 2 | Core Routing & Disruption | Engineer พัฒนา Module 2 และ 3 เชื่อมต่อโหนดผ่าน NetworkX / Specialist ป้อนค่า Latency อ้างอิงจริง เช่น RTT โลก–ดวงจันทร์ / Tester/QA เริ่มเขียน Test Case เบื้องต้น |
| Week 3 | QoS & Integration | Engineer พัฒนา Module 4 และประกอบ Toy Model ครบถ้วน / Tester/QA ทดสอบ Store-and-Forward และ QoS Priority / DevOps ตั้งค่า CI/CD Pipeline |
| Week 4 | Testing & Pitch Prep | Tester/QA ทำ Stress Test เช่น Packet Loss 90%, Node Failure / Engineer + DevOps แก้ไข Bug ที่พบ |

## 4.2 บทบาทและความรับผิดชอบของทีม (Roles & Responsibilities Matrix)

| บทบาท | ความรับผิดชอบหลัก | ความรับผิดชอบรอง | อำนาจตัดสินใจ |
|------|------------------|------------------|---------------|
| Architect | รัฐภูมิ | ออกแบบสถาปัตยกรรม Mesh/DTN ทั้งระบบ, จัดทำเอกสาร Architecture Spec | อนุมัติ Code Review, ติดตาม Technical Debt | ตัดสินใจ Technology Stack และ Architecture |
| Engineer | กิตติพัฒน์ | เขียนโค้ดจำลองระบบ, พัฒนา Routing Algorithm, Optimization | แก้ไข Bug, จัดทำ Code Documentation | วิธีการเขียนโค้ดและโครงสร้าง Internal |
| Specialist | ภัทราพร | วิจัยข้อจำกัดอวกาศ (Latency, Interference), ให้ข้อมูลเชิงลึก | จัดทำเอกสารเชิงเทคนิค, ทดสอบในฐานะผู้เชี่ยวชาญ | Domain Logic และทิศทางอ้างอิงวิทยาศาสตร์ |
| DevOps | ชุตินันท์ | ตั้งค่า CI/CD Pipeline, บริหาร Version Control (Git) | เขียนสคริปต์ Deploy, จัดการ Environment | เลือก Tools เช่น Docker, GitHub และ Branch Strategy |
| Tester/QA | ธนพัฒน์ | สร้าง Test Case, ทดสอบ Performance, รายงาน Bug | ทดสอบ UAT, รีวิวความถูกต้องของเอกสาร | เกณฑ์ผ่าน Quality Gate และความพร้อม Release |

## 4.3 เกณฑ์การยอมรับระบบ (Acceptance Criteria)
ก่อนนำเสนอในวัน Project Pitch ระบบต้องผ่านเกณฑ์ต่อไปนี้:

1. ระบบสามารถจำลองการส่งข้อมูลระหว่างโหนดอย่างน้อย 3 โหนดได้สำเร็จในสภาวะสัญญาณปกติ
2. เมื่อโหนดปลายทางถูก Offline ข้อมูลจะต้องถูกเก็บใน Buffer โดยไม่สูญหาย (0% Data Loss)
3. เมื่อโหนดปลายทางกลับมา Online ระบบต้องส่งข้อมูลที่ค้างอยู่ออกอัตโนมัติโดยไม่ต้องสั่งใหม่
4. ระบบ QoS ต้องส่งข้อมูล Priority 1 (Critical) ออกก่อน Priority 2 และ 3 เสมอ ไม่ว่าลำดับการรับเข้า Buffer จะเป็นอย่างไร
5. โค้ดผ่าน Unit Test ครบทุก Module ด้วย pytest โดยไม่มี FAILED

## 4.4 Test Scenarios สำหรับ Tester/QA
กรณีทดสอบหลักที่ต้องดำเนินการก่อนการนำเสนอ:

| ชื่อ Test Case | วิธีทดสอบ | ผลลัพธ์ที่คาดหวัง |
|---------------|-----------|------------------|
| TC-01: Normal Transmission | ส่งข้อมูลทุก Priority เมื่อทุกโหนด Online | ข้อมูลถึงปลายทางทันที ไม่มีการ Store |
| TC-02: Single Node Failure | ปิดโหนด Lunar Gateway กะทันหัน | ข้อมูลถูก Store ใน Buffer ของ Earth Control |
| TC-03: Full Recovery | เปิดโหนดกลับมา หลังจาก Store ไปแล้ว | ข้อมูล Forward อัตโนมัติ เรียง Priority ถูกต้อง |
| TC-04: QoS Priority Test | ส่ง Media ก่อน Critical เมื่อสัญญาณขาด | Critical ต้องถูก Forward ก่อน Media เสมอ |
| TC-05: Stress Test 90% | ตั้งค่า Packet Loss เป็น 90% | ระบบยังส่ง Critical ได้ครบ ไม่มี Data Loss |