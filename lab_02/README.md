# Lab 02 — Robust Reactive Lamp

เอกสารสำหรับแจกนักศึกษา: [คู่มือ Lab 02 ฉบับ Word](Lab02_Student_Manual_TH.docx)

แล็บนี้ใช้ simulator เปรียบเทียบ controller สี่แบบภายใต้ input trajectory เดียวกัน แล้ววัดผลด้วยข้อมูลจาก repeated trials ก่อนนำแนวคิดไปเชื่อมกับหุ่นยนต์จริง

> ค่า threshold, gain, noise, delay และ command limit ในโฟลเดอร์นี้เป็น **proposed course model** สำหรับการเรียนการสอน ไม่ใช่ค่าความปลอดภัยหรือค่าที่รับรองสำหรับฮาร์ดแวร์จริง

## 1. Research question

รูปแบบ controller และระดับ sensor uncertainty ส่งผลต่อความเร็ว ความถูกต้อง และความเสถียรของการตอบสนองอย่างไร

## 2. ไฟล์สำคัญ

- `lab02.py` — simulator, controller C0–C3, protocol และ metric reference
- `student_controller.py` — โครงเริ่มต้นที่ให้นักศึกษาเติม TODO 1–4; simulator เรียกใช้ได้ด้วย `--controller-source student`
- `grade_submission.py` — ตรวจพฤติกรรมโค้ดนักศึกษาแยกตามฟังก์ชันและทดลองครบ C0–C3
- `plot_trial.py` — สร้างกราฟระยะ, state และ command จาก CSV หนึ่ง trial
- `tests/` — ตรวจ reference, การเชื่อม student controller และกรณี TODO ยังไม่เสร็จ
- `requirements.txt` — dependency สำหรับสร้างกราฟ

## 3. เตรียมสภาพแวดล้อม

ใช้ Python 3.10 ขึ้นไป จากโฟลเดอร์นี้:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

การจำลองและสร้าง CSV ใช้ Python standard library ส่วน `matplotlib` ใช้เฉพาะตอนสร้างกราฟ

## 4. งานก่อนทดลอง

1. เมื่อ noise เพิ่มขึ้น C1 จะมี switching count เปลี่ยนอย่างไร

คาดว่า switching count ของ C1 จะเพิ่มขึ้น เนื่องจาก C1 ใช้ Single Threshold ที่ค่า 0.35 m เพียงค่าเดียว เมื่อค่าจาก sensor มี noise และแกว่งอยู่ใกล้ threshold ค่าระยะอาจสลับข้าม threshold ไปมา ทำให้สถานะ FAR และ NEAR เปลี่ยนสลับกันหลายครั้ง


2. C2 จะลด false trigger โดยแลกกับ latency หรือ recovery time อย่างไร

คาดว่า C2 จะสามารถลด false trigger และการสลับสถานะที่ไม่จำเป็นได้ เนื่องจากใช้ Low-pass Filter ร่วมกับ Hysteresis โดยกำหนด T_enter = 0.32 m และ T_exit = 0.38 m ทำให้ค่าจาก sensor ต้องผ่าน threshold ที่แตกต่างกันก่อนเปลี่ยนสถานะ

อย่างไรก็ตาม การกรองข้อมูลและ hysteresis จะทำให้ controller ใช้เวลามากขึ้นก่อนเปลี่ยนสถานะ จึงคาดว่า latency หรือ recovery time จะสูงกว่า C1


3. เมื่อเพิ่ม sensor delay เส้น command จะเลื่อนจาก physical event เท่าใด

คาดว่าเมื่อเพิ่ม sensor delay การตอบสนองของ controller จะเกิดช้ากว่า physical event ใกล้เคียงกับค่าของ delay ที่เพิ่มเข้าไป เช่น หากเพิ่ม delay 300 ms การตอบสนองควรช้าลงประมาณ 0.3 s
## 5. ทำความเข้าใจ input scenario

ทุก trial ยาว 20 วินาทีและใช้ trajectory เดียวกัน:

| เวลา | ระยะจริงจำลอง |
|---|---|
| 0–4 s | 0.60 m |
| 4–8 s | เคลื่อนเข้าใกล้จนถึง 0.25 m |
| 8–12 s | ค้างใกล้พร้อม disturbance ขนาดเล็ก |
| 12–16 s | เคลื่อนออกจนถึง 0.60 m |
| 16–20 s | 0.60 m |

โปรแกรมเพิ่ม Gaussian noise และ delay เฉพาะเส้นทาง sensor ส่วน `true_distance_m` ยังคงเป็น ground truth สำหรับวิเคราะห์ผล

## 6. Controller ที่ต้องเปรียบเทียบ

| Condition | หลักการ | ค่า input ที่ใช้ |
|---|---|---|
| C0 | Open-loop sequence ตามเวลา | ไม่ใช้ sensor |
| C1 | Single threshold ที่ `T = 0.35 m` | raw distance |
| C2 | Low-pass filter และ hysteresis | filtered distance |
| C3 | Proportional response และ clamp | filtered distance |

ให้เปิด `student_controller.py` และเติม TODO 1–4 ก่อนอ่านส่วน implementation ใน `lab02.py` โดยเมธอดแต่ละตัวต้องคืนค่าที่คำนวณได้ ตัวเชื่อมใน `lab02.py` จะจัดการ state, filter history และการส่ง command ให้ simulator

มีสองโหมดที่ใช้ input, seed และ metric ชุดเดียวกัน:

- `--controller-source reference` (ค่าเริ่มต้น) ใช้ตัวอย่างใน `lab02.py`
- `--controller-source student` ใช้ `StudentController` ในไฟล์ที่ระบุด้วย `--student-file` (ค่าเริ่มต้นคือ `student_controller.py` ในโฟลเดอร์นี้)

ไฟล์เริ่มต้นยังมี TODO จึงรันโหมด student ไม่ผ่านจนกว่านักศึกษาจะเติมฟังก์ชันครบ

## 7. ขั้นทดลอง A — เปรียบเทียบ C0–C3

ค่าเริ่มต้นใช้ `sigma = 0.01 m`, delay `0 ms` และ 5 trials ต่อ condition รวม 20 trials:

```powershell
python lab02.py --protocol controller-comparison --out results\comparison
```

เมื่อเติม TODO แล้ว ให้รันโค้ดนักศึกษาในโฟลเดอร์ผลแยกจาก reference:

```powershell
python lab02.py --controller-source student --protocol controller-comparison `
  --student-file student_controller.py --out results\student_comparison
```

`run_config.json` จะบันทึก `controller_source`, ที่อยู่ไฟล์นักศึกษา และ SHA-256 ของไฟล์เพื่อระบุว่า CSV ชุดนั้นสร้างจาก submission ใด

ไฟล์ที่ได้:

```text
results/comparison/
├── run_config.json
├── summary_trials.csv
├── summary_aggregate.csv
└── trials/
    ├── C0_*.csv
    ├── C1_*.csv
    ├── C2_*.csv
    └── C3_*.csv
```

ตรวจ `run_config.json` ก่อนวิเคราะห์เพื่อยืนยัน parameter, seed และจำนวน trial

## 8. ขั้นทดลอง B — Noise และ delay

หลังจากขั้น A ให้เลือก controller หนึ่งแบบ โดยค่าเริ่มต้นแนะนำ C2 เพราะต้องการศึกษาผลของ filter และ hysteresis

### ชุดย่อในคาบ

ห้า combinations และ 3 trials ต่อ combination รวม 15 trials:

```powershell
python lab02.py --protocol robustness-short --condition C2 --out results\c2_short
```

### ชุดเต็มหลังเรียน

noise `0.00, 0.01, 0.03 m` คูณ delay `0, 100, 300 ms` และ 5 trials รวม 45 trials:

```powershell
python lab02.py --protocol robustness-full --condition C2 --out results\c2_full
```

หากต้องการทดลองซ้ำในโฟลเดอร์เดิม ต้องระบุ `--overwrite` อย่างชัดเจน โปรแกรมจะไม่เขียนทับผลเดิมโดยอัตโนมัติ

## 9. สร้างกราฟหนึ่ง trial

เลือกไฟล์ CSV จาก `trials`:

```powershell
python plot_trial.py results\comparison\trials\C2_n0.01_d000_r01.csv `
  --out results\comparison\C2_trial1.png
```

กราฟต้องอ่านร่วมกันสองส่วน:

- ระยะจริง, raw distance, filtered distance และ threshold
- state, command และตำแหน่ง event

ชี้บนกราฟว่า stimulus ข้าม criterion เวลาใด และ controller เริ่มตอบสนองเวลาใด

## 10. Metric ที่โปรแกรมคำนวณ

- `latency_enter_s` และ `latency_exit_s` — เวลาจาก physical crossing ถึง state ถูกต้องครั้งแรก
- `recovery_time_s` — เวลาจาก physical threshold crossing จนเริ่มช่วงที่ state ถูกต้องต่อเนื่องอย่างน้อย 0.5 s โดยรายงานค่าที่มากกว่าระหว่าง enter และ exit
- `false_trigger_rate_per_min` — การเข้าสู่ NEAR ขณะที่ ground truth ยังเป็น FAR ต่อ valid observation minute
- `switching_count` — จำนวนการเปลี่ยน FAR กับ NEAR ทั้งหมด
- `extra_switches` — switching count ที่เกิน expected transitions สองครั้ง
- `mean_abs_command_change` — ค่าเฉลี่ย `|u[k] - u[k-1]|`
- `invalid_sample_count` — จำนวน sample ที่ missing, non-finite หรือ out of range

ต้องอ่านหลาย metric ร่วมกัน ตัวอย่างเช่น command ที่ไม่เคลื่อนเลยอาจมี smoothness ดี แต่ไม่ตอบสนองต่อ stimulus

## 11. คำถามวิเคราะห์ผล

 1. C1 และ C2 แตกต่างกันอย่างไรในเรื่อง latency, false trigger และ extra switching?

จากผลการทดลองพบว่า C1 ตอบสนองได้เร็วกว่า C2 อย่างชัดเจน แต่มีความไวต่อ noise สูงกว่า

C1 มี Enter latency ≈ 0.0189 s และ Exit latency ≈ 0.0291 s ขณะที่ C2 มี Enter latency ≈ 0.4069 s และ Exit latency ≈ 0.4531 s

ในด้านความเสถียร C1 มี extra switches เฉลี่ย 12.4 ครั้ง และ false trigger rate ≈ 8.39 ครั้ง/นาที ส่วน C2 มี extra switches = 0 และ false trigger = 0

ดังนั้น C1 มีข้อดีคือสามารถตอบสนองได้รวดเร็ว แต่มีโอกาสเกิด chatter หรือการสลับ state ซ้ำ ๆ ใกล้ threshold ส่วน C2 ใช้ Low-pass Filter และ Hysteresis จึงมีความทนทานต่อ noise มากกว่า แต่ต้องแลกกับ response latency ที่สูงขึ้น


 2. เมื่อเพิ่ม noise จาก 0.01 m เป็น 0.03 m metric ใดเปลี่ยนชัดที่สุด?

พิจารณาผลของ C2 ที่ delay = 0 ms พบว่า:

- noise = 0.01 m: Enter latency ≈ 0.4309 s และ Exit latency ≈ 0.4171 s
- noise = 0.03 m: Enter latency ≈ 0.4069 s และ Exit latency ≈ 0.3531 s

ค่า Enter latency เปลี่ยนประมาณ 0.0240 s ขณะที่ Exit latency เปลี่ยนประมาณ 0.0640 s

ดังนั้น metric ที่เปลี่ยนชัดที่สุดในผลการทดลองนี้คือ Exit latency โดยลดลงจากประมาณ 0.4171 s เป็น 0.3531 s หรือเปลี่ยนประมาณ 0.0640 s

อย่างไรก็ตาม ไม่ควรสรุปว่า noise ที่มากขึ้นทำให้ controller ทำงานดีขึ้น เนื่องจากผลนี้เป็นผลจาก simulation และชุด trial ที่ทำการทดลอง ในขณะเดียวกัน C2 ยังคงรักษา false trigger = 0 และ extra switches = 0 ได้ทั้งสองระดับ noise


 3. เมื่อเพิ่ม sensor delay เป็น 300 ms latency เพิ่มใกล้เคียง 300 ms หรือไม่?

ใช่ จากผลของ C2 ที่ noise = 0.00 m พบว่าเมื่อเพิ่ม sensor delay จาก 0 ms เป็น 300 ms ค่า Enter latency เพิ่มจากประมาณ 0.4229 s เป็น 0.7229 s ซึ่งเพิ่มขึ้นประมาณ 0.3000 s

ในส่วนของ Exit latency เพิ่มจากประมาณ 0.4171 s เป็น 0.7171 s ซึ่งเพิ่มขึ้นประมาณ 0.3000 s เช่นเดียวกัน

ดังนั้นผลการทดลองแสดงให้เห็นว่า sensor delay 300 ms ทำให้ response latency เพิ่มขึ้นใกล้เคียง 300 ms จริง


 4. C3 ชน command limit ช่วงใด และ smoothness สัมพันธ์กับ tracking error อย่างไร?

จากการตรวจผล C3 ทั้ง 5 trials พบว่าค่า |command| สูงสุดมีค่าประมาณ:

- r01 = 0.5282
- r02 = 0.5194
- r03 = 0.5324
- r04 = 0.5187
- r05 = 0.5243

โดยค่าที่สูงที่สุดคือประมาณ 0.5324 ใน trial r03 ซึ่งยังต่ำกว่า command limit ที่กำหนดไว้ที่ ±0.6

ดังนั้น C3 ไม่เกิด command saturation ในการทดลองนี้

สำหรับความ smooth ของ command พบว่า MeanAbsCommandChange อยู่ประมาณ 0.00455–0.00470 ในทั้ง 5 trials ซึ่งมีค่าใกล้เคียงกัน แสดงว่า command มีการเปลี่ยนแปลงค่อนข้างต่อเนื่อง

ส่วน MeanAbsTrackingError ซึ่งคำนวณเพิ่มเติมจากค่าเฉลี่ยของ |0.35 - filtered_distance| อยู่ประมาณ 0.161–0.162 m

ผลนี้แสดงให้เห็นว่า command ที่ smooth ไม่ได้หมายความว่า tracking error จะต่ำเสมอ เนื่องจาก smoothness และ tracking error เป็น metric ที่วัดคุณสมบัติของ controller คนละด้านกัน


 5. มี invalid sample หรือไม่ และระบบจัดการอย่างไร?

ในการทดลอง controller-comparison ของ C0–C3 พบว่า invalid_sample_count_mean = 0 ทุก condition จึงไม่มี invalid sample ในชุดการทดลองนี้

อย่างไรก็ตาม ในการทดลอง robustness-full ของ C2 เมื่อมี sensor delay พบ invalid sample ในช่วงเริ่มต้นของ simulation โดยมีค่าเฉลี่ยดังนี้:

- Delay 0 ms = 0 samples
- Delay 100 ms = 5 samples
- Delay 300 ms = 15 samples

เมื่อ sensor sample เป็น invalid หรือ stale controller จะเรียกใช้ safe_command() และกำหนด command = 0.0 เพื่อป้องกันไม่ให้ระบบใช้ข้อมูล sensor ที่ไม่ถูกต้องในการควบคุม

แนวทางนี้ช่วยให้ controller อยู่ในสถานะปลอดภัยเมื่อยังไม่มีข้อมูล sensor ที่สามารถใช้งานได้ และส่วน invalid sample นี้ผ่านการตรวจจาก grade_submission.py แล้ว

## 12. เชื่อมต่อกับหุ่นยนต์จริง

เปลี่ยนเฉพาะสามจุดใน experiment loop:

1. `true_distance_m()` เปลี่ยนเป็น reference measurement หรือเว้นว่างหากไม่มี ground truth
2. sensor simulator เปลี่ยนเป็น `read_distance_m()` ที่คืนค่าและ sensor timestamp
3. normalized command เปลี่ยนเป็นคำสั่ง actuator หลังตรวจหน่วย, mechanical limit และทิศทางเครื่องหมาย

ก่อนจ่ายกำลังให้ actuator:

- ตรวจ datasheet, min/max range และ field of view ของ sensor
- ตรวจ joint limit, velocity limit และ command unit
- ทดสอบ `safe_command()` และ emergency stop
- เริ่มด้วย command limit ต่ำกว่าค่าทดลองจริง
- ยึดหุ่นยนต์และกันพื้นที่เคลื่อนที่

ห้ามใช้ parameter จาก simulator กับหุ่นยนต์โดยตรงโดยไม่ทำขั้นตอนเหล่านี้

## 13. ผลส่งมอบ

แต่ละกลุ่มส่ง:

1. Prediction ก่อนทดลอง
2. Block diagram ของ sensorimotor loop พร้อมทิศทางข้อมูลและ feedback
3. `student_controller.py` ที่เติม TODO และ source code อื่นที่แก้
4. ผลตรวจ `grade_submission.py`, `run_config.json` ของโหมด student, raw CSV ทุก trial และ `summary_aggregate.csv`
5. กราฟตัวแทนอย่างน้อย C1 และ C2 พร้อมเวลา physical crossing และ first correct response
6. รายงาน 1–2 หน้า พร้อมข้อจำกัดของการทดลอง

## 14. ตรวจงานนักศึกษา

จากโฟลเดอร์ `lab_02` ผู้สอนใช้คำสั่งต่อไปนี้กับไฟล์ที่แต่ละกลุ่มส่ง โดยแยกชื่อรายงานและโฟลเดอร์ผลต่อกลุ่ม:

```powershell
python grade_submission.py --student-file path\to\student_controller.py `
  --out results\group01_grade.json
python lab02.py --controller-source student `
  --student-file path\to\student_controller.py `
  --protocol controller-comparison --out results\group01_trials
```

รายงานตรวจการโหลดไฟล์, filter, threshold, hysteresis, proportional/clamp, invalid sample และการรันเต็ม C0–C3 หากยังมี TODO จะรายงาน FAIL และคืน exit code 1 ผลตรวจนี้เป็นเพียงหลักฐานด้าน controller ไม่ใช่คะแนน 20 คะแนนอัตโนมัติ ผู้สอนยังต้องตรวจ block diagram, ความซื่อสัตย์ของข้อมูล, การวิเคราะห์ และการตีความ

การนำไฟล์ Python ที่นักศึกษาส่งมารันคือการรันโค้ดของผู้ส่ง ควรตรวจใน VM หรือสภาพแวดล้อมแยกที่ไม่มี token, credential หรือข้อมูลส่วนตัว และอย่ารันด้วยสิทธิ์สูง
