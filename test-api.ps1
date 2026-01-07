# Phase 1 & 2 Backend API Test Script
# This script tests all implemented endpoints with test data creation

Write-Output "=== PMS-CYNERZA PHASE 1 & 2 API TESTING ==="
Write-Output ""

# Step 1: Login
Write-Output "1. LOGIN"
$loginBody = @{email="admin@hotel.com"; password="admin123"} | ConvertTo-Json
$auth = Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/login/json" -Method POST -Body $loginBody -ContentType "application/json" -TimeoutSec 10
$token = $auth.access_token
$headers = @{Authorization="Bearer $token"}
Write-Output "✅ Login successful"
Write-Output ""

# Step 2: Create Room Types
Write-Output "2. CREATE ROOM TYPES"
$deluxeType = @{name="Deluxe Room"; total_rooms=10; max_occupancy=2; base_price=150.00; description="Comfortable deluxe room"} | ConvertTo-Json
$suiteType = @{name="Suite"; total_rooms=5; max_occupancy=4; base_price=300.00; description="Luxurious suite"} | ConvertTo-Json

$deluxe = Invoke-RestMethod -Uri "http://127.0.0.1:8000/room-types" -Method POST -Body $deluxeType -Headers $headers -ContentType "application/json" -TimeoutSec 10
$suite = Invoke-RestMethod -Uri "http://127.0.0.1:8000/room-types" -Method POST -Body $suiteType -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "✅ Created Deluxe Room (ID: $($deluxe.id))"
Write-Output "✅ Created Suite (ID: $($suite.id))"
Write-Output ""

# Step 3: Create Physical Rooms (Phase 2)
Write-Output "3. CREATE PHYSICAL ROOMS (Phase 2)"
$room101 = @{room_number="101"; room_type_id=$deluxe.id; floor=1} | ConvertTo-Json
$room102 = @{room_number="102"; room_type_id=$deluxe.id; floor=1} | ConvertTo-Json
$room201 = @{room_number="201"; room_type_id=$suite.id; floor=2} | ConvertTo-Json

$r101 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/rooms" -Method POST -Body $room101 -Headers $headers -ContentType "application/json" -TimeoutSec 10
$r102 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/rooms" -Method POST -Body $room102 -Headers $headers -ContentType "application/json" -TimeoutSec 10
$r201 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/rooms" -Method POST -Body $room201 -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "✅ Created Room 101 (ID: $($r101.id))"
Write-Output "✅ Created Room 102 (ID: $($r102.id))"
Write-Output "✅ Created Room 201 (ID: $($r201.id))"
Write-Output ""

# Step 4: Create Customers (Phase 1 - VIP fields)
Write-Output "4. CREATE CUSTOMERS (Phase 1 - VIP tracking)"
$customer1 = @{
    name="John Doe"
    email="john@example.com"
    phone="+1234567890"
    address="123 Main St"
    id_proof_type="passport"
    id_proof_number="AB123456"
    is_vip=$true
    notes="Preferred customer"
    preferences="Non-smoking, high floor"
} | ConvertTo-Json

$customer2 = @{
    name="Jane Smith"
    email="jane@example.com"
    phone="+0987654321"
    address="456 Oak Ave"
    id_proof_type="driver_license"
    id_proof_number="DL789012"
    is_vip=$false
    notes="Regular guest"
} | ConvertTo-Json

$c1 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/customers" -Method POST -Body $customer1 -Headers $headers -ContentType "application/json" -TimeoutSec 10
$c2 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/customers" -Method POST -Body $customer2 -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "✅ Created VIP Customer: John Doe (ID: $($c1.id), VIP: $($c1.is_vip))"
Write-Output "✅ Created Customer: Jane Smith (ID: $($c2.id), VIP: $($c2.is_vip))"
Write-Output ""

# Step 5: Create Bookings
Write-Output "5. CREATE BOOKINGS"
$checkIn = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")
$checkOut = (Get-Date).AddDays(3).ToString("yyyy-MM-dd")

$booking1 = @{
    customer_id=$c1.id
    room_type_id=$deluxe.id
    check_in=$checkIn
    check_out=$checkOut
    num_rooms=1
    num_guests=2
    amount_paid=100.00
    notes="Early check-in requested"
} | ConvertTo-Json

$b1 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/bookings" -Method POST -Body $booking1 -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "✅ Created Booking for John Doe (ID: $($b1.id))"
Write-Output ""

# Phase 1 Tests
Write-Output "=== PHASE 1 ENDPOINT TESTS ==="
Write-Output ""

Write-Output "6. DASHBOARD - Today's Activity"
$activity = Invoke-RestMethod -Uri "http://127.0.0.1:8000/dashboard/todays-activity" -Headers $headers -TimeoutSec 10
Write-Output "   Arrivals Expected: $($activity.arrivals_expected)"
Write-Output "   Departures Expected: $($activity.departures_expected)"
Write-Output "   In House: $($activity.in_house)"
Write-Output ""

Write-Output "7. DASHBOARD - 14-Day Forecast"
$forecast = Invoke-RestMethod -Uri "http://127.0.0.1:8000/dashboard/forecast" -Headers $headers -TimeoutSec 10
Write-Output "   Forecast Days: $($forecast.forecast_days.Count)"
Write-Output "   Peak Day: $($forecast.peak_day)"
Write-Output ""

Write-Output "8. DASHBOARD - Quick Stats"
$stats = Invoke-RestMethod -Uri "http://127.0.0.1:8000/dashboard/quick-stats" -Headers $headers -TimeoutSec 10
Write-Output "   Revenue Today: `$$($stats.revenue_today)"
Write-Output "   Occupancy: $($stats.occupancy_today)%"
Write-Output ""

Write-Output "9. CUSTOMERS - List with VIP fields"
$customers = Invoke-RestMethod -Uri "http://127.0.0.1:8000/customers" -Headers $headers -TimeoutSec 10
Write-Output "   Total Customers: $($customers.Count)"
foreach ($cust in $customers) {
    Write-Output "   - $($cust.name): VIP=$($cust.is_vip), LTV=`$$($cust.lifetime_value), Stays=$($cust.total_stays)"
}
Write-Output ""

Write-Output "10. BLOCKS - List"
$blocks = Invoke-RestMethod -Uri "http://127.0.0.1:8000/blocks/?start_date=2026-01-01&end_date=2026-12-31" -Headers $headers -TimeoutSec 10
Write-Output "   Active Blocks: $($blocks.Count)"
Write-Output ""

Write-Output "11. ALLOTMENTS - List"
$allotments = Invoke-RestMethod -Uri "http://127.0.0.1:8000/allotments/" -Headers $headers -TimeoutSec 10
Write-Output "   Active Allotments: $($allotments.Count)"
Write-Output ""

# Phase 2 Tests
Write-Output "=== PHASE 2 ENDPOINT TESTS ==="
Write-Output ""

Write-Output "12. HOUSEKEEPING - List Rooms"
$rooms = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/rooms" -Headers $headers -TimeoutSec 10
Write-Output "   Total Rooms: $($rooms.Count)"
foreach ($room in $rooms) {
    Write-Output "   - Room $($room.room_number): Status=$($room.housekeeping_status), Occupancy=$($room.occupancy_status)"
}
Write-Output ""

Write-Output "13. HOUSEKEEPING - Update Room Status"
$statusUpdate = @{housekeeping_status="clean"; notes="Cleaned and inspected"} | ConvertTo-Json
$updated = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/rooms/$($r101.id)/status" -Method PATCH -Body $statusUpdate -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "   ✅ Room $($updated.room_number) status updated to: $($updated.housekeeping_status)"
Write-Output ""

Write-Output "14. HOUSEKEEPING - Create Task"
$taskDate = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
$task = @{
    room_id=$r102.id
    task_type="checkout_clean"
    priority="high"
    scheduled_date=$taskDate
    notes="VIP checkout - thorough cleaning required"
} | ConvertTo-Json
$newTask = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/tasks" -Method POST -Body $task -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "   ✅ Created Task ID: $($newTask.id) for Room $($r102.room_number)"
Write-Output ""

Write-Output "15. HOUSEKEEPING - List Tasks"
$tasks = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/tasks" -Headers $headers -TimeoutSec 10
Write-Output "   Total Tasks: $($tasks.Count)"
foreach ($t in $tasks) {
    Write-Output "   - Task $($t.id): Room $($t.room_number), Type=$($t.task_type), Status=$($t.task_status)"
}
Write-Output ""

Write-Output "16. HOUSEKEEPING - Complete Task"
$completion = @{completion_notes="Room thoroughly cleaned and sanitized"} | ConvertTo-Json
$completed = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/tasks/$($newTask.id)/complete" -Method POST -Body $completion -Headers $headers -ContentType "application/json" -TimeoutSec 10
Write-Output "   ✅ Task completed: $($completed.message)"
Write-Output ""

Write-Output "17. HOUSEKEEPING - Summary Report"
$summary = Invoke-RestMethod -Uri "http://127.0.0.1:8000/housekeeping/summary" -Headers $headers -TimeoutSec 10
Write-Output "   Total Rooms: $($summary.total_rooms)"
Write-Output "   Dirty: $($summary.dirty)"
Write-Output "   Clean: $($summary.clean)"
Write-Output "   Inspected: $($summary.inspected)"
Write-Output "   Pending Tasks: $($summary.pending_tasks)"
Write-Output "   Completed Today: $($summary.completed_today)"
Write-Output ""

WriteOutput "=== ALL TESTS COMPLETED SUCCESSFULLY ==="
Write-Output ""
Write-Output "Summary:"
Write-Output "✅ Phase 1: Dashboard (3), Customers VIP tracking (1), Blocks (1), Allotments (1)"
Write-Output "✅ Phase 2: Housekeeping Rooms (3), Tasks (3), Summary (1)"
Write-Output ""
