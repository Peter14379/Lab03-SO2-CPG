# ใบงาน Lab 06 — Student

**เรื่อง:** Lamp Emotion and Interaction — Finite State Machine (FSM)

ชื่อ/รหัสนักศึกษา: ____________________

กลุ่ม: ____________________

วันที่: ____________________

**ขอบเขต:** การทดลองทั้งหมดเป็น Proposed Course Model ใช้ข้อมูลเซนเซอร์สังเคราะห์และคำสั่ง Output ในซอฟต์แวร์ ไม่ใช่ผลวัดจาก Robot Lamp จริง ไม่มีระบบ Learning และไม่มีการปรับ Parameter แบบถาวร

**เงื่อนไขที่เลือก:** Baseline Transition Contract

## 1. Prediction ก่อนรัน

คาดว่า C0 ซึ่งไม่มี Debounce และ Hysteresis จะได้รับผลกระทบจากสัญญาณ Bounce ของปุ่มกดและ Noise ของเซนเซอร์ระยะทางมากกว่า C1 ทำให้ C0 อาจรับเหตุการณ์ซ้ำและเปลี่ยนสถานะบ่อยโดยไม่จำเป็น

ส่วน C1 มี Debounce สำหรับ Button และ Touch และใช้ Hysteresis สำหรับ Near และ Approach จึงคาดว่าจะลดการเปลี่ยนสถานะที่เกิดจากสัญญาณรบกวนได้ แต่มีโอกาสเพิ่มความล่าช้าของการตอบสนอง เนื่องจากต้องรอให้สัญญาณผ่านเงื่อนไขก่อน

สำหรับเหตุการณ์ที่ไม่ควรมี Onset ใหม่ ได้แก่ Touch ขณะที่ระบบอยู่ในสถานะ Afraid ซึ่งจะถูก Guard ป้องกันไว้ และ Fault ที่เกิดขณะระบบอยู่ในสถานะ Normal และ Output เป็น Neutral อยู่แล้ว ทำให้ไม่มีการเปลี่ยน Motion หรือ RGB ใหม่

ตัวชี้วัดหลักในการทดลอง ได้แก่ State Transitions, Both Onset Count, จำนวนการตอบสนองภายใน 1 วินาที, No-both-onset Count และ Max Observed Latency

**หมายเหตุด้านลำดับการทดลอง:** ข้อความนี้เป็นการระบุสมมติฐานจากกลไกที่คาดการณ์ไว้ เพื่อใช้เปรียบเทียบผล ไม่ได้อ้างว่ามีการบันทึกเป็นหลักฐานก่อนรันในครั้งที่นำโปรแกรมมาคำนวณซ้ำ

## 2. FSM Diagram และเงื่อนไขการเปลี่ยนสถานะ

FSM ประกอบด้วย 5 สถานะ คือ `normal`, `interested`, `happy`, `afraid` และ `sleepy`

### 2.1 การเปลี่ยนสถานะ

- `normal → interested` เมื่อเกิด Button หรือ Approach
- `normal → happy` เมื่อเกิด Touch
- `normal → sleepy` เมื่อไม่มี Interaction ตามเวลา Idle 6 s
- `interested → normal` เมื่อเกิด Timeout หลังอยู่ในสถานะ Active 2 s
- `happy → normal` เมื่อเกิด Timeout หลังอยู่ในสถานะ Active 2 s
- `sleepy → interested` เมื่อเกิด Button หรือ Approach
- `sleepy → happy` เมื่อเกิด Touch
- ทุกสถานะ `→ afraid` เมื่อเกิด Near
- ทุกสถานะ `→ normal` เมื่อเกิด Clear หรือ Fault

### 2.2 Guard และ Recovery

เมื่อระบบอยู่ในสถานะ `afraid` จะไม่เปลี่ยนสถานะตาม Touch, Button, Approach, Timeout หรือ Idle โดยใช้ Guard เพื่อให้ระบบคงสถานะกลัวไว้จนกว่าจะเกิด Clear หรือ Fault

เมื่อเกิด Fault ระบบจะใช้สถานะ Normal เป็น Fallback หากระบบอยู่ใน Normal อยู่แล้วและไม่มี Output Expression ใหม่ เหตุการณ์นั้นจะมีสถานะ `no_state_change` และค่า Onset Latency เป็น N/A

เมื่อไม่มี Interaction ขณะอยู่ใน Normal เป็นเวลา 6 s ระบบจะเข้าสู่ Sleepy และสามารถกลับมา Interested ได้เมื่อกด Button

### 2.3 Output ของแต่ละสถานะ

| State | Tilt (rad) | Extend (rad) | Nod (rad) | RGB |
|---|---:|---:|---:|---|
| normal | 0 | 0 | 0 | (60,90,140) |
| interested | 0.22 | 0.18 | 0.06 | (255,180,0) |
| happy | 0.10 | 0.10 | 0.18 sin(2πt) | (40,220,80) |
| afraid | −0.22 | −0.22 | −0.16 | (230,30,30) |
| sleepy | 0 | −0.15 | −0.20 | (50,40,100) |

ค่า t ใน Happy คือเวลาหลังเข้าสู่สถานะ โดยทุกการเคลื่อนไหวถูกจำกัดด้วย Bounds และ Slew Rate ตามแบบจำลอง

## 3. ตาราง Transition 5 States × 8 Events

| Current State | fault | near | clear | touch | button | approach | timeout | idle |
|---|---|---|---|---|---|---|---|---|
| normal | normal | afraid | normal | happy | interested | interested | Hold | sleepy |
| interested | normal | afraid | normal | happy | interested | interested | normal | Hold |
| happy | normal | afraid | normal | happy | interested | interested | normal | Hold |
| afraid | normal | afraid | normal | Hold | Hold | Hold | Hold | Hold |
| sleepy | normal | afraid | normal | happy | interested | interested | Hold | Hold |

**Hold** หมายถึง `transition()` คืนค่า `None` เพื่อไม่สร้าง Transition ใหม่ ส่วนการคืนชื่อสถานะเดิม เช่น interested เมื่อได้รับ Button ในขณะอยู่ Interested อยู่แล้ว อาจถูกบันทึกเป็น `no_state_change`

### 3.1 Event Priority

ลำดับความสำคัญคือ

**fault > near > clear > touch > button > approach > timeout > idle**

หากมีหลาย Event ที่ผ่านการตรวจใน Tick เดียวกัน ระบบจะเลือก Event ที่มี Priority สูงสุด ส่วน Event ที่มี Priority ต่ำกว่าจะถูกบันทึกเป็น `discarded_priority`

กรณี Near และ Touch เกิดพร้อมกัน หากทั้งคู่ Recognized ใน Tick เดียวกัน Near ต้องชนะ เพราะมี Priority สูงกว่า Touch

อย่างไรก็ตาม หาก Touch และ Near ผ่าน Filter คนละ Tick อาจเกิดสถานะชั่วคราวได้ก่อน Near จะถูกรับรู้ จึงต้องตรวจ Recognized Time และ Actual Application Time จาก CSV ไม่ใช่พิจารณา Source Time เพียงอย่างเดียว

## 4. เติม TODO และตรวจ Checker

เลือกใช้ Baseline Contract ของอาจารย์ โดยแก้ฟังก์ชัน `transition()` ใน `student_policy.py` ให้รองรับทั้ง 40 State/Event Combinations

คำสั่งตรวจ:

`py -3 check_submission.py`

ผล Checker หลังแก้ไข:

- Checked 40 transition pairs
- Contract = baseline
- Failures = 0
- PASS: transition contract complete

### Failed Case ที่ใช้แก้ Logic

ก่อนแก้ไขพบว่า `normal + touch` คืนค่า `None` แต่ตาม Baseline Contract ต้องคืนค่า `happy` เพื่อให้โคมไฟตอบสนองต่อการสัมผัส

หลังเพิ่มเงื่อนไข `if event == "touch": return "happy"` โดยวางไว้หลัง Afraid Guard ทำให้ Touch เปลี่ยนเข้าสู่ Happy ได้จากทุกสถานะยกเว้น Afraid

นอกจากนี้ยังเติม Timeout สำหรับ Interested/Happy และ Idle สำหรับ Normal จนครบทุกกรณี

Starter Checker มี Failures ทั้งหมด 7 กรณี และหลังแก้ครบจึงผ่าน 40 คู่

## 5. เปรียบเทียบ C0 และ C1 ด้วย Paired Seeds

### 5.1 Protocol

ใช้ Python 3.11 ที่รองรับการรันโปรแกรม, dt = 0.02 s, Duration = 22 s และ Scheduler Delay = 0.04 s

C1 ใช้ Debounce 0.06 s สำหรับ Button และ Touch พร้อม Hysteresis สำหรับ Near และ Approach ส่วน C0 ไม่มี Debounce/Hysteresis

ใช้ Seeds 41, 42 และ 43 โดย C0/C1 ใช้ชุด Synthetic Inputs เดียวกันสำหรับแต่ละ Seed และใช้ Baseline Policy เหมือนกันทุกกรณี

### 5.2 ตารางผลการทดลอง

| Condition/Seed | All Inputs | Both Onset | ≤1 s Both | No Both Onset / Status | Max Latency (s) | Transitions |
|---|---:|---:|---:|---|---:|---:|
| C0/41 | 10 | 7 | 7 | 3: discarded_priority 1, no_state_change 2 | 0.24 | 67 |
| C1/41 | 10 | 7 | 7 | 3: policy_held 1, no_state_change 2 | 0.14 | 9 |
| C0/42 | 10 | 6 | 6 | 4: filtered_not_recognized 1, preempted_before_apply 1, no_state_change 2 | 0.18 | 72 |
| C1/42 | 10 | 7 | 7 | 3: policy_held 1, no_state_change 2 | 0.14 | 10 |
| C0/43 | 10 | 6 | 6 | 4: discarded_priority 1, no_state_change 3 | 0.04 | 63 |
| C1/43 | 10 | 7 | 7 | 3: policy_held 1, no_state_change 2 | 0.14 | 9 |

### 5.3 วิเคราะห์ผล

ผลการทดลองแสดงว่า C1 ลดจำนวน State Transitions ได้มากกว่า C0 โดย C0 มีจำนวน Transitions เท่ากับ 67, 72 และ 63 สำหรับ Seeds 41, 42 และ 43 ตามลำดับ ขณะที่ C1 มีเพียง 9, 10 และ 9 ครั้ง

จึงสนับสนุนว่า Debounce และ Hysteresis ช่วยลดผลกระทบจากสัญญาณรบกวนในแบบจำลองนี้

เมื่อพิจารณา Both Onset พบว่า C1 ตอบสนองได้ 7 จาก 10 External Inputs ในทุก Seed ส่วน C0 ตอบสนองได้ 7, 6 และ 6 จาก 10 Inputs

สำหรับ Expected Set ตาม Baseline ที่ประกาศก่อนรัน มีทั้งหมด 7 IDs ต่อ Seed ได้แก่

`button_01`, `touch_01`, `approach_01`, `clear_01`, `near_01`, `clear_02`, `button_02`

ผล Primary Pass ภายใน 1 s คือ C0 ได้ 7/7, 6/7 และ 6/7 ส่วน C1 ได้ 7/7 ทั้งสาม Seeds

### 5.4 Negative Result

แม้ C1 ลดการเปลี่ยนสถานะได้มาก แต่ไม่ได้ตอบสนองเร็วกว่า C0 ทุกกรณี เพราะ Debounce เพิ่มเวลาในการรับรู้บาง Event เช่น Button และ Touch

นอกจากนี้ C0 ใน Seed 43 มี Max Observed Latency เพียง 0.04 s ซึ่งต่ำกว่า C1 ที่ 0.14 s แต่ C0 ยังมี External Input ที่ไม่มี Both Onset 4 รายการ จึงไม่ควรใช้ Max Observed Latency เพียงตัวเดียวตัดสินประสิทธิภาพทั้งหมด

การทดลองทั้งสาม Seeds เป็น Synthetic Replications ไม่ใช่การทดลองจริงที่เป็นอิสระทางกายภาพ

## 6. ตรวจ Latency จาก Source ถึง Onset

### 6.1 ตาราง Event Timing — ตรวจจาก CSV จริงของผู้จัดทำ

ข้อมูลจาก `results/completed/events_C1_r01.csv` เงื่อนไข C1, Seed 41 ซึ่งตรวจด้วย `Import-Csv` บนเครื่องผู้จัดทำ โดยแสดง 3 เหตุการณ์แรกที่มีหลักฐานยืนยันครบทุกฟิลด์ ได้แก่ Source, Recognized, Decision, Queue, Apply, Motion Onset และ RGB Onset

| Input ID | Source (s) | Recognized (s) | Decision (s) | Queued (s) | Actual Apply (s) | Motion Onset (s) | RGB Onset (s) | Both Latency (s) | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| C1/button_01 | 1.00 | 1.10 | 1.10 | 1.10 | 1.14 | 1.14 | 1.14 | 0.14 | responded |
| C1/touch_01 | 3.00 | 3.06 | 3.06 | 3.06 | 3.10 | 3.10 | 3.10 | 0.10 | responded |
| C1/approach_01 | 5.00 | 5.00 | 5.00 | 5.00 | 5.04 | 5.04 | 5.04 | 0.04 | responded |

ทั้งสามเหตุการณ์มี `pass_1s_both = True` และเริ่มสร้าง Output Motion และ RGB ในแบบจำลองพร้อมกัน ในกรณี Button มีระยะเวลา Source → Recognized 0.10 s ขณะที่ Approach รับรู้ได้ทันที และทุกกรณีใช้เวลาอีก 0.04 s จาก Decision ถึง Actual Apply/Onset ตามผลที่บันทึกได้

ตารางนี้ใช้ข้อมูลจากไฟล์ CSV ของผู้จัดทำโดยตรง ส่วนตัวอย่าง Near/Touch Conflict และ Fault ในข้อ 7 เป็นผลวิเคราะห์ประกอบจากการทดลองก่อนหน้า และควรตรวจแถวเหตุการณ์ใน CSV ของผู้จัดทำเพิ่มเพื่อยืนยันรายละเอียดระดับ Event

### 6.2 ตัวอย่างคำนวณ Latency จากข้อมูลจริง

เลือก Event `button_01` ของ C1 Seed 41:

- Source Time = 1.00 s
- Recognized Time = 1.10 s
- Decision Time = 1.10 s
- Queued Time = 1.10 s
- Actual Application Time = 1.14 s
- First Motion Onset = 1.14 s
- First RGB Onset = 1.14 s

สูตร: `Both Latency = max(First Motion Onset, First RGB Onset) − Source Time`

แทนค่า: `max(1.14, 1.14) − 1.00 = 0.14 s`

แยกองค์ประกอบเวลา: Source → Recognized = 0.10 s; Recognized → Decision = 0.00 s; Decision → Actual Apply = 0.04 s; Actual Apply → Onset = 0.00 s รวม **0.14 s** ตรงกับ `both_latency_s` ใน Events CSV

ตรวจเพิ่ม: `touch_01` ได้ `3.10 − 3.00 = 0.10 s` และ `approach_01` ได้ `5.04 − 5.00 = 0.04 s` ตรงกับข้อมูล CSV เช่นกัน

### 6.3 ข้อจำกัดของการวัด Latency

Latency นี้วัดจากการเปลี่ยน Output ที่ถูก Apply ภายในแบบจำลอง ไม่ใช่ Physical Motion หรือ LED Onset ของอุปกรณ์จริง

หากต้องการวัด Hardware Latency ต้องใช้นาฬิกาที่สอบเทียบร่วมกันและอุปกรณ์วัด เช่น กล้องความเร็วสูงหรือ Photodiode พร้อมระบุ Resolution และ Measurement Uncertainty

## 7. Conflict, Fault, Quiet และ Recovery

### 7.1 Near + Touch Conflict

ที่เวลา 7.00 s มี Near และ Touch จาก Synthetic Sources เดียวกัน

สำหรับ C1 Seed 41 พบว่า Near ถูก Recognized ที่เวลา 7.00 s และเปลี่ยนระบบเข้าสู่ Afraid พร้อม Output Onset ที่ 7.04 s

Touch ถูก Recognized ภายหลังที่ 7.06 s ขณะที่ระบบอยู่ใน Afraid จึงถูก Guard ป้องกันไว้ และได้รับสถานะ `policy_held` โดยไม่มี Motion/RGB Onset ใหม่

สำหรับ C0 Seed 41 Touch ถูกบันทึกเป็น `discarded_priority` เพราะ Near มี Priority สูงกว่าใน Tick เดียวกัน

ผลนี้แสดงว่า Priority และ State Guard ทำงานต่างระดับกัน และต้องพิจารณา Timing ก่อนสรุปเหตุการณ์

### 7.2 Stale และ Invalid Fallback

กรณี Invalid Distance ที่ 11.00 s และ Stale Touch ที่ 12.00 s ถูกแปลงเป็น Fault Event และใช้ Fallback ไปยังสถานะ Normal

ใน C1 Seed 41 ระบบอยู่ใน Normal อยู่แล้ว จึงไม่มี State Change หรือ Output Expression ใหม่

ทั้งสองกรณีได้รับสถานะ `no_state_change` และค่า Both Latency เป็น N/A ซึ่งไม่ควรแทนด้วย 0 s

### 7.3 Quiet-to-Sleepy

หลังจากไม่มี Interaction ตามช่วงเวลาที่กำหนด ระบบเกิด Internal Idle ที่เวลา 15.00 s ทำให้เปลี่ยนจาก Normal เป็น Sleepy และมี Motion/RGB Onset ที่ 15.04 s

เหตุการณ์นี้เป็น Internal Timeout Logic ของแบบจำลอง ไม่ใช่หนึ่งใน External Inputs 10 รายการ จึงต้องแยกจากการคำนวณ External Response Rate

### 7.4 Recovery Button

ที่เวลา 18.00 s เกิด `button_02` ขณะระบบอยู่ใน Sleepy

สำหรับ C1 Seed 41 ปุ่มผ่าน Debounce และถูก Recognized ที่เวลา 18.06 s ก่อนเปลี่ยนสถานะเป็น Interested พร้อม Motion/RGB Onset ที่เวลา 18.10 s

จึงได้ Both Latency = 18.10 − 18.00 = 0.10 s

เหตุการณ์นี้แสดงว่าระบบสามารถกลับมาตอบสนองหลังเข้าสู่ Sleepy ตาม Baseline Policy

### 7.5 ความแตกต่างของ Status

| Status | ความหมาย |
|---|---|
| discarded_priority | Event มี Priority ต่ำกว่า Event อื่นใน Tick เดียวกัน |
| policy_held | FSM คืนค่า Hold เพราะ Guard หรือไม่อนุญาตให้เปลี่ยนสถานะ |
| no_state_change | ไม่มี State/Expression ใหม่ที่ต้อง Apply |
| filtered_not_recognized | Input ไม่ผ่านเงื่อนไขการรับรู้ของ Filter |
| preempted_before_apply | คำสั่งถูกคำสั่งใหม่แทนก่อน Apply |
| preempted_partial | คำสั่งเริ่มมีผลบางส่วนก่อนถูกแทน |
| censored_end | สิ้นสุดเวลาการทดลองก่อนสังเกต Onset ได้ครบ |
| responded | พบ Output Onset ตามเกณฑ์ของ Event |

การไม่มี Onset อาจเกิดจากหลายสาเหตุและต้องบันทึกสถานะตามจริง ไม่ควรนำทุกกรณีไปนับเป็น Latency 0 s

## 8. ตรวจ Replay และ Reproducibility

ใช้คำสั่ง Replay:

`py -3 lab06.py --policy student --condition C1 --repeats 1 --replay results/completed/inputs_r01.csv --output-dir results/replay`

ตรวจเปรียบเทียบไฟล์

- `results/completed/raw_C1_r01.csv`
- `results/replay/raw_C1_r01.csv`
- `results/completed/events_C1_r01.csv`
- `results/replay/events_C1_r01.csv`

### ผลการตรวจ Replay บนเครื่องผู้จัดทำ

ผู้จัดทำรัน Replay ของ C1 ด้วย `results/completed/inputs_r01.csv` แล้วเปรียบเทียบ SHA-256 ของไฟล์คู่ด้วย PowerShell ผลที่ปรากฏจริงใน Terminal คือ:

| ไฟล์เปรียบเทียบ | ผลตรวจ |
|---|---|
| `raw_C1_r01.csv` (completed vs replay) | **MATCH** |
| `events_C1_r01.csv` (completed vs replay) | **MATCH** |

ทั้ง Raw และ Events CSV ตรงกันแบบ Byte-for-byte ตามการเปรียบเทียบ Hash ที่ผู้จัดทำรันจริง โดยยังไม่ได้บันทึกค่า Hex SHA-256 ลงในใบงานนี้ เพราะผลหน้าจอแสดงเฉพาะ MATCH ไม่ได้แสดง Digest

หาก Replay ต่างกันให้ตรวจ Policy, Configuration, Source Version, Input File Hash และการแก้ไขโค้ดก่อนสรุปว่าเกิดจากความสุ่ม ค่า Seed ใน Replay เป็น N/A เพราะใช้ Input ที่บันทึกไว้แล้วแทนการสุ่มใหม่

## 9. สรุปผลและเตรียมรายงาน

### 9.1 Prediction เทียบกับผลจริง

ผลการทดลองสนับสนุน Prediction ที่ว่า C1 ช่วยลดการเปลี่ยนสถานะจากสัญญาณรบกวน โดยจำนวน State Transitions ของ C1 ต่ำกว่า C0 มากในทุก Seed

อย่างไรก็ตาม C1 ไม่ได้ตอบสนองเร็วกว่า C0 ทุก Event เพราะการใช้ Debounce เพิ่มเวลาตรวจสอบสัญญาณ เช่น Button ใน Seed 41 มี Both Latency 0.14 s สำหรับ C1 เทียบกับ 0.04 s สำหรับ C0

จึงต้องพิจารณาทั้งความถี่ของการเปลี่ยนสถานะ ความสามารถในการตอบสนอง และเหตุการณ์ที่ไม่มี Onset ร่วมกัน

### 9.2 ข้อจำกัดของแบบจำลอง

การทดลองทั้งหมดใช้ Synthetic Inputs และ Simulated Outputs โดยแกน Tilt, Extend และ Nod เป็นการกำหนดเชิงความหมาย ไม่ใช่แบบจำลองกลไกที่มี Torque, Linkage, Collision หรือ Motor Dynamics จริง

ระบบไม่มี Learning และไม่ได้เปลี่ยน Parameter แบบถาวร การเปลี่ยนสถานะตามกฎของ FSM จึงไม่ถือว่าเป็น Machine Learning

ผล Simulated Onset ภายใน 1 s ยังไม่สามารถยืนยันการตอบสนองของ Servo และ RGB จริงได้ และไม่ใช่การรับรอง Hardware Safety

### 9.3 Negative Result

ผล Negative Result ที่สำคัญคือ C1 มี Latency ของ Button สูงกว่า C0 เนื่องจาก Debounce และในบางกรณี C0 มี Max Observed Latency ต่ำกว่า C1 แต่มี No-both-onset มากกว่า

นอกจากนี้ Touch Conflict และ Fault ที่เกิดขณะ Output เป็น Neutral อาจไม่มี Onset ใหม่ตามที่ระบบออกแบบไว้ ซึ่งเป็นผลที่ต้องรายงาน ไม่ควรตัดข้อมูลออกเพื่อให้ Response Rate สูงขึ้น

### 9.4 หลักฐานสำหรับส่ง

- [x] อธิบาย Prediction และ Architecture
- [x] วาด FSM และระบุ Guard/Timeout/Recovery
- [x] ตาราง 5 States × 8 Events
- [x] เติม Baseline Policy และรัน Checker บนเครื่องผู้จัดทำ ผ่าน 40/40 คู่
- [x] ตาราง C0/C1 ครบ Seeds 41, 42, 43 จากผลทดลองบนเครื่องผู้จัดทำ
- [x] ตาราง Latency จาก `events_C1_r01.csv` ของผู้จัดทำ พร้อมตัวอย่างคำนวณ
- [x] วิเคราะห์ Conflict, Fallback, Quiet และ Recovery
- [x] ตรวจ Replay จาก CSV ต้นฉบับและพบ MATCH ทั้ง Raw/Events
- [x] รันบนเครื่องผู้จัดทำและสร้าง Raw CSV, Events, Metrics, Config และ Manifest ใน `results/completed` และ `results/replay`
- [ ] แนบกราฟจาก `trace_C0_r01.svg` และ `trace_C1_r01.svg`
- [ ] จัดทำรายงาน Word 1–2 หน้า
- [ ] Commit และ Push งานขึ้น GitHub

**คำสั่งรันบน Windows**

`py -3 check_submission.py`

`py -3 lab06.py --policy student --condition all --repeats 3 --output-dir results/completed`

`py -3 lab06.py --policy student --condition C1 --repeats 1 --replay results/completed/inputs_r01.csv --output-dir results/replay`

**สรุปท้ายใบงาน**

Lab 06 แสดงให้เห็นว่า Finite State Machine ร่วมกับ Debounce และ Hysteresis สามารถช่วยลดการเปลี่ยนสถานะที่เกิดจากสัญญาณรบกวนในแบบจำลอง Robot Lamp ได้ โดยยังต้องแลกกับความล่าช้าในการรับรู้เหตุการณ์บางประเภท และบาง Input อาจไม่มี Output Onset ใหม่ตามการออกแบบของระบบ

ผลทั้งหมดเป็นเพียง Proposed Course Model และ Synthetic Replications ไม่ใช่ผลจาก Servo, RGB หรือเซนเซอร์จริง จึงยังไม่สามารถใช้ยืนยัน Physical Latency, Hardware Safety หรือประสิทธิภาพของหุ่นยนต์จริงได้โดยตรง
