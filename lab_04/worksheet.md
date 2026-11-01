# Lab 04 — Artificial Hormone Mechanism

ชื่อ/รหัส: นาย ปีเตอร์ ประสิทธิพร 6752500070  
กลุ่ม: __________  
วันที่: 1/11/2569  
code version/hash (SHA256): `98F0515A7E9932999CEFE3E58A1C14C84C75BDBBACB9034CDA22041941A84345`

## A. แบบจำลองและการคาดการณ์

> หากไม่ได้บันทึก prediction ไว้ก่อนรัน ให้ระบุส่วนนี้ว่าเป็น **การวิเคราะห์ย้อนหลังจากแบบจำลอง** และไม่ควรอ้างว่าเป็น prediction ที่เขียนก่อนทดลอง

โครงสร้างของระบบที่ใช้ใน Lab 04 คือ

```text
Stimulus S
    ↓
Production P
    ↓
Hormone state H
    ↓
Receptor R
    ↓
Bounded mapping
    ↓
phi_rad / stride_half_m
```

โดยค่า `S` ส่งผลโดยตรงต่อ production `P` ส่วน clearance `C` และ binding `B` คำนวณจากสถานะเก่าของระบบ จากนั้นจึงอัปเดตค่า hormone `H` เพียงครั้งเดียวในแต่ละ step และ receptor จะอ่านค่า `H` ใหม่เพื่อคำนวณค่า `R`

ค่า `R` ถูกนำไปใช้กับ bounded mapping เพื่อคำนวณคำสั่ง `phi_rad` และ `stride_half_m`

Lab 04 นี้ยัง **ไม่ได้จำลอง CPG หรือ gait โดยตรง** แต่เป็นการตรวจพฤติกรรมของ artificial hormone mechanism และ interface ที่จะส่งค่าต่อไปยังระบบ CPG

จากแบบจำลองคาดว่า

- เมื่อเพิ่ม production ค่า `H` จะเพิ่มขึ้นเร็วขึ้น
- เมื่อลด clearance ค่า `H` จะลดลงช้าลงหลัง stimulus ปิด
- เมื่อตัด binding พฤติกรรมการสะสมและการฟื้นตัวของ `H` จะเปลี่ยน
- C0 เป็น direct mapping โดยใช้ `R = S` และไม่มี hormone state `H`

เนื่องจาก `H` มี upper bound เท่ากับ 1 การเปรียบเทียบเฉพาะค่า peak อาจไม่สามารถแยกความแตกต่างของแต่ละ condition ได้ทั้งหมด จึงต้องใช้ metric เช่น AUC, rise time, recovery time และ clamp fraction ร่วมด้วย

---

## B. ตรวจคำนวณสอง Update แรกของ C1

ใช้ค่าพารามิเตอร์

```text
dt = 0.05 s
k_prod = 0.8
k_clear = 0.6
k_bind = 0.2
```

stimulus เริ่มเปิดที่

```text
input_time_s = 10.00 s
```

ผลการคำนวณสอง update แรก:

| input_time_s | time_s | P | C | B | H_raw = H_new | R_new | phi (rad) | stride (m) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10.00 | 10.05 | 0.8000 | 0.0000 | 0.0000 | 0.0400 | 0.0400 | 0.20800 | 0.055400 |
| 10.05 | 10.10 | 0.8000 | 0.0240 | 0.0080 | 0.0784 | 0.0784 | 0.21568 | 0.055784 |

ในการ update ที่สอง ใช้ค่า `H_old = 0.04` สำหรับคำนวณทั้ง clearance และ binding ก่อนคำนวณค่า `H` ใหม่

ลำดับการคำนวณในหนึ่ง step คือ

```text
H_old, R_old
      ↓
P, C, B
      ↓
H_raw
      ↓
Clamp H
      ↓
H_new
      ↓
R_new
      ↓
phi / stride
```

time convention ที่ใช้คือ `input_time_s` เป็นเวลาที่ใช้เลือก stimulus สำหรับรอบคำนวณ ส่วน `time_s` เป็นเวลาหลังจาก update state แล้วหนึ่ง step ดังนั้น input ที่เวลา `10.00 s` จะสร้าง state ที่เวลา `10.05 s`

---

## C. Controlled Comparison — Step Profile

รันเงื่อนไข C0–C4 โดยใช้ `dt`, duration, initial hormone state, stimulus และ mapping เดียวกัน

ผลจาก metrics:

| Condition | Peak H | AUC H | Latency (s) | Rise 10–90% (s) | Recovery (s) | Upper clamp fraction | phi TV (rad) |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 | N/A | N/A | 0.05 | 0.00 | 0.05 | N/A | 0.4000 |
| C1 | 0.9997 | 9.9996 | 0.15 | 2.70 | 2.85 | 0.000 | 0.3998 |
| C2 | 1.0000 | 10.6724 | 0.10 | 1.05 | 2.85 | 0.290 | 0.3999 |
| C3 | 1.0000 | 11.3891 | 0.15 | 1.45 | 5.10 | 0.273 | 0.3979 |
| C4 | 1.0000 | 10.7547 | 0.15 | 1.70 | 3.80 | 0.258 | 0.3995 |

C0 ไม่มี hormone state `H` เนื่องจากใช้ direct mapping `R = S` ดังนั้น `Peak H` และ `AUC H` จึงรายงานเป็น `N/A` ไม่ใช่ศูนย์

ค่า latency และ recovery ของ C0 ที่ `0.05 s` เกิดจากความละเอียดของ log แบบ post-update ซึ่งใช้ `dt = 0.05 s`

### การเปรียบเทียบผล

C3 มี recovery เท่ากับ `5.10 s` ส่วน C1 มี recovery เท่ากับ `2.85 s`

ดังนั้น C3 ฟื้นช้ากว่า C1

```text
5.10 - 2.85 = 2.25 s
```

C1–C4 มีค่า peak H ใกล้เคียง 1 เนื่องจาก hormone มี upper bound เท่ากับ 1 จึงไม่ควรใช้ peak เพียง metric เดียวในการเปรียบเทียบ

C3 มีค่า `AUC H = 11.3891` ซึ่งสูงที่สุด และมี recovery time สูงที่สุดที่ `5.10 s` ขณะที่ C2 มี latency สั้นที่สุดในกลุ่ม hormone model ที่ `0.10 s`

ดังนั้น metric เช่น AUC, rise time, recovery time และ upper clamp fraction สามารถใช้แยกพฤติกรรมของแต่ละ condition ได้ดีกว่าการดู peak เพียงอย่างเดียว

ค่า `phi TV` ที่ต่ำกว่าเพียงอย่างเดียวไม่สามารถใช้ยืนยันว่า gait มีคุณภาพดีกว่าได้ เนื่องจาก Lab 04 ไม่ได้จำลอง gait หรือ dynamic stability โดยตรง

---

## D. Extreme Profiles และ Fault Handling

รัน C1 ด้วย extreme profiles จำนวน 4 แบบ:

- `zero`
- `one`
- `spike`
- `fault`

ผลที่ได้:

| Profile | Peak H | AUC H | Fault count | ข้อสังเกต |
|---|---:|---:|---:|---|
| zero | 0.000 | 0.000 | 0 | H และ R คงที่ศูนย์ |
| one | 1.000 | 28.750 | 0 | stimulus คงที่ตลอดการทดลอง |
| spike | 0.040 | 0.050 | 0 | stimulus เปิดหนึ่ง sample ที่ 10.00 s |
| fault | 0.9831 | 8.7699 | 1 | พบ fault หนึ่งครั้งและ reset ตาม protocol |

### Zero profile

เมื่อ stimulus เป็นศูนย์ตลอดการทดลอง ค่า H และ R ยังคงเป็นศูนย์ แสดงว่าไม่มี hormone production เกิดขึ้นโดยไม่มี stimulus

### One profile

เมื่อ stimulus เป็น 1 ตลอดการทดลอง ค่า H เพิ่มจนถึง upper bound ที่ 1 และมี `AUC H = 28.750`

### Spike profile

เมื่อ stimulus เปิดเพียงหนึ่ง sample ที่เวลา `10.00 s` ค่า Peak H เท่ากับ `0.040` และ AUC H เท่ากับ `0.050`

### Fault profile

พบ fault จำนวน 1 ครั้ง

ที่ state เวลา `15.05 s` ระบบควรมีสถานะ

```text
fault = 1
H = 0
R = 0
phi = 0.20 rad
stride = 0.055 m
```

หลังจาก fault สิ้นสุด ระบบสามารถเริ่มสะสม H ใหม่ได้เมื่อ stimulus กลับมาเป็นค่าปกติ

### Software bounds และ Hardware safety

software bounds, actuator limits และ emergency stop เป็นคนละส่วนกัน

- software bounds จำกัดค่าที่โปรแกรมอนุญาตให้ส่งออก
- actuator limits เป็นข้อจำกัดทางกายภาพของ actuator จริง
- emergency stop เป็นระบบหยุดฉุกเฉินของระบบจริง

ดังนั้น software bounds ไม่สามารถใช้แทน hardware safety ได้

---

## E. Week 03 → Lab 04 Handoff

Lab 04 ใช้ bounded mapping ที่ส่งต่อมาจาก Lab 03:

```text
phi_cmd = clamp(0.20 + 0.20R, 0.10, 0.45) rad
```

และ

```text
stride_half = clamp(0.055 + 0.010R, 0.040, 0.070) m
```

เมื่อ

```text
R = 0
```

จะได้

```text
phi = 0.20 rad
stride_half = 0.055 m
```

เมื่อ

```text
R = 1
```

จะได้

```text
phi = 0.40 rad
stride_half = 0.065 m
```

ทั้งสองกรณียังอยู่ภายใน bounds ที่กำหนดไว้จาก Lab 03

---

## F. สรุปผลและข้อจำกัด

ผลการทดลองแสดงให้เห็นว่าการเปลี่ยน production, clearance และ binding ส่งผลต่อ temporal response ของ hormone model แม้ว่าหลาย condition จะมี peak H ใกล้ 1 เนื่องจากใช้ upper bound เดียวกัน

C2 มี latency สั้นที่สุดในกลุ่ม hormone model ที่ `0.10 s` ส่วน C3 มี recovery time สูงที่สุดที่ `5.10 s` และมี AUC H สูงที่สุดประมาณ `11.3891` แสดงให้เห็นว่าการดู peak เพียงค่าเดียวไม่เพียงพอสำหรับอธิบาย dynamics ของระบบ

Extreme profiles แสดงว่าระบบตอบสนองตามที่กำหนดสำหรับ `zero`, `one`, `spike` และ `fault` โดย fault handling สามารถ reset state และเริ่มกลับมาทำงานได้หลังจาก input กลับสู่สภาวะปกติ

ค่าพารามิเตอร์ hormone และ bounded mapping ใน Lab 04 เป็น **proposed course model** สำหรับการเรียนการสอน ไม่ใช่ค่าที่รับรองสำหรับ hardware จริง

Lab 04 ไม่ได้จำลอง CPG หรือ gait โดยตรง และผลการทดลองนี้จึงไม่สามารถใช้ยืนยัน dynamic stability, ground contact force, energy consumption, motor torque, actuator limits หรือ hardware safety ได้

การตรวจการเชื่อมต่อกับ CPG, gait และ hardware จริงต้องทำแยกต่างหากในขั้นตอนถัดไป

## Checklist

- [x] `student_hormone.py` เติม TODO 1 และ TODO 2
- [x] `check_submission.py` ผ่านทุก test
- [x] comparison C0–C4
- [x] comparison CSV 5 files
- [x] extreme profiles 4 แบบ
- [x] extreme CSV 4 files
- [x] metrics
- [x] handoff mapping
- [ ] plots
- [ ] report 1–2 หน้า
- [ ] บันทึกคำสั่งรันซ้ำ
- [ ] commit / code version ที่ใช้ส่ง