# Retry export lab

แบบฝึกหัดสำหรับ Grok Bot Chief → Engineer → Cursor Cloud Agent → pstack → evidence → PR
นี่เป็นตัวอย่างเพื่อการเรียนรู้ ไม่ใช่โค้ดหรือ configuration ส่วนตัวของ Lauren Tan

## เริ่มทดลอง

Python 3.9+ และ Git; ใช้ Python standard library เท่านั้น ไม่มี database/API key/dev server
รันจาก root repository:

```bash
python3 -m unittest -v
python3 verify_runtime.py
sh .cursor/install-lab.sh
```

Baseline: first-export unit test ผ่าน 1 test แต่ runtime retry check **ต้อง fail**
เพราะ actual มี 7 records แทน 3 records นี่คือบั๊กที่ตั้งใจให้ agent แก้ในแบบฝึกหัด
CI บน main จะแดงที่ runtime check ตามโจทย์ ห้ามแก้ expected/fixtures ให้เขียว

## Acceptance และขอบเขต

- A1: first export มี 1/Ada และ 2/Lin
- A2: retry first.csv ไม่เพิ่มแถวและไม่เปลี่ยน bytes
- A3: next.csv เพิ่ม 3/Grace เพียงครั้งเดียว
- A4: รักษาค่าเก่า/order/header; first occurrence wins แม้มี Changed-Lin/Ignored-Grace
- valid CSV id/name, sequential requests, one writer; ไม่รวม concurrency/updates/crash recovery

## GitHub issue และ Chief

Issue ตัวอย่างติด label `chief-ready` สำหรับให้ Chief อ่านจาก repository นี้
การสร้าง issue ไม่เปิด Grok routine ให้เอง ต้องตั้ง Chief login/skill/hourly routine แล้วตรวจ history
ให้ Chief เตรียม brief และรอคน dispatch; ไม่เปิด workerซ้ำ ไม่ merge/deploy/เพิ่มงบ

## ขั้นถัดไปใน Cursor

1. ติดตั้ง/ตรวจ pstack และ cursor-team-kit บนบัญชีของคุณ
2. สร้าง repo verification skill จาก CLI นี้บน baseline แล้ว commit/push
3. ตั้ง Cloud Environment จาก repoนี้ ให้ install command ใช้ `sh .cursor/install-lab.sh`
4. ตรวจ /setup-pstack ใน cloud, model mapping, plugin dependencies และ fresh preflight
5. ตั้ง Chief auto intake สำหรับ open issue ที่มี chief-ready → dispatch งานเดียว
6. จบที่ draft PR พร้อม implementation และ fresh-verifier evidence ของ proposed head

Environment/Build, plugins, models และ routine **ยังไม่ได้ตั้งหรือทดลองบัญชีจริง** เพียงเพราะ repoนี้สร้างแล้ว
Cloud runner ต้องติดตั้ง Python 3.9+ และ Git; install scriptตรวจ tools ไม่ได้ติดตั้ง packageแทนคุณ
