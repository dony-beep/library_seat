import requests
import datetime
import csv
import os

URL = "https://lib.inha.ac.kr/pyxis-api/1/seat-rooms?smufMethodCode=PC&roomTypeId=3&branchGroupId=1"
FILENAME = "library_seats.csv"

def classify_occupancy(occupied, total):
    if total == 0:
        return "알수없음"
    rate = (occupied / total) * 100
    if rate >= 70:
        return "혼잡"
    elif rate < 30:
        return "여유"
    else:
        return "보통"

def fetch_and_save_once():
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("API 요청 실패:", e)
        return 1

    if not data.get("success"):
        print("API 실패:", data.get("message"))
        return 1

    # 현재 시간 (UTC -> KST)
    now_utc = datetime.datetime.utcnow()
    now = now_utc + datetime.timedelta(hours=9)

    # 실행 시간을 0분 또는 30분 단위로 내림(보정)
    minute = (now.minute // 30) * 30
    scheduled_time = now.replace(minute=minute, second=0, microsecond=0)

    timestamp = scheduled_time.strftime("%Y-%m-%d %H:%M:%S")
    weekday = scheduled_time.strftime("%A")

    file_exists = os.path.isfile(FILENAME)
    with open(FILENAME, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["날짜", "요일", "열람실명", "전체좌석", "사용중", "잔여좌석", "혼잡도"])

        for room in data["data"]["list"]:
            name = room.get("name", "")
            seats = room.get("seats", {})
            total = seats.get("total", 0) or 0
            occupied = seats.get("occupied", 0) or 0
            remaining = total - occupied
            occupancy_class = classify_occupancy(occupied, total)
            writer.writerow([timestamp, weekday, name, total, occupied, remaining, occupancy_class])

    return 0

if __name__ == "__main__":
    exit(fetch_and_save_once())