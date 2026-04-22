# ====================== CONSTANTS ======================
INVENTORY_FILE = "1_inventory.txt"
SUPPLIER_FILE = "2_suppliers.txt"
SALES_FILE = "3_sales.txt"
REFUNDS_FILE = "4_refunds.txt"
PAYMENTS_FILE = "5_payments.txt"
ORDERS_FILE = "6_orders.txt"
EMPLOYEE_FILE = "7_employee.txt"
CUSTOMER_FILE = "8_customer.txt"

# Status constants
STATUS_PENDING = "Pending"
STATUS_DELIVERED = "Delivered"
# Status constants
STATUS_PAID = "Paid"
STATUS_UNPAID = "Unpaid"
LOW_STOCK_LEVEL = 5


# ====================== MAIN SYSTEM FUNCTIONS ======================
# ====================== ACCOUNT MANAGEMENT ======================
def ShopTrack_main():
    while True:
        print("\n================ ShopTrack SYSTEM =================")
        print("1. Add Employee")
        print("2. Login")
        print("3. Exit System")
        print("---------------------------------------------------")
        choice = input("Please choose[1/2/3]: ")
        if choice == "1":
            add_employee()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Thank you for using ShopTrack. Goodbye!")
            return
        else:
            print("Invalid choice.")
            continue


def add_employee():
    print("\n===================================================")
    print("Add Employee")
    print("---------------------------------------------------")

    username = input("Enter username: ")
    print("1. Administrator")
    print("2. Cashier")
    print("3. Accountant")
    print("4. Stock Manager")
    print("5. Supplier")
    role_choice = input("Enter role [1-5]: ")

    # Map role choice to role name
    role_mapping = {
        "1": "Administrator",
        "2": "Cashier",
        "3": "Accountant",
        "4": "Stock Manager",
        "5": "Supplier"
    }
    role = role_mapping.get(role_choice)

    if not role:
        print("Invalid role selection.")
        return

    # 密码输入验证
    while True:
        raw_password = input("Enter password: ")
        confirm_password = input("Confirm password: ")

        if raw_password != confirm_password:
            print("Passwords do not match. Please try again.")
            continue

        if len(raw_password) < 6:
            print("Password must be at least 6 characters.")
            continue

        break

    contact_info = input("Enter contact info (phone number): ")
    join_date = input("Enter join date (YYYY-MM-DD): ")

    if not all([username, role, raw_password, contact_info, join_date]):
        print("Error: All fields are required.")
        return

    employee_id = generate_unique_id("EMP", EMPLOYEE_FILE)
    if not employee_id:
        print("Error generating employee ID.")
        return

    # 使用纯Python哈希函数
    password_hash = simple_hash_password(raw_password)
    status = "active"

    new_record = f"{employee_id},{username},{role},{password_hash},{contact_info},{join_date},{status}\n"
    try:
        with open(EMPLOYEE_FILE, 'a') as f:
            f.write(new_record)
        print("Employee added successfully.")
    except Exception as e:
        print(f"Error updating file: {e}")


def login():
    print("\n===================================================")
    print("Login")
    print("---------------------------------------------------")
    print("(Enter 'back' at any time to return to main menu)")

    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        username = input("Enter your username: ")
        if username.lower() == "back":
            print("Returning to main menu...")
            return

        password = input("Enter your password: ")
        if password.lower() == "back":
            print("Returning to main menu...")
            return

        valid, role = validate_credentials(username, password)
        if valid:
            print(f"Welcome {username} ({role})")
            # Direct to role-specific menu based on stored role
            if role == "Administrator":
                admin_menu()
            elif role == "Cashier":
                cashier_menu()
            elif role == "Accountant":
                accountant_menu()
            elif role == "Stock Manager":
                stock_manager_menu()
            elif role == "Supplier":
                supplier_menu()
            else:
                print("Unknown role. Contact admin.")
            return
        else:
            attempts += 1
            if attempts < max_attempts:
                print("Invalid username or password. Try again.")
            else:
                print("Account locked. Contact admin for unlock.")
                return


def validate_credentials(username, password):
    """使用纯Python验证凭据"""
    try:
        with open(EMPLOYEE_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 4 and data[1] == username:
                    stored_hash = data[3]
                    if simple_hash_password(password) == stored_hash:
                        return True, data[2]  # Return validation result and role
        return False, None
    except FileNotFoundError:
        print("Employee file not found.")
        return False, None


def simple_hash_password(raw_password):
    """纯Python实现的简单哈希函数"""
    total = 0
    for ch in raw_password:
        total += ord(ch)  # 将每个字符的ASCII值相加
    return hex(total)[2:].zfill(16)  # 转换为16进制并填充到16位


def generate_unique_id(prefix, filename):
    """生成唯一ID"""
    try:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            with open(filename, 'w') as f:
                f.write("")
            lines = []

        if lines:
            last_id = lines[-1].split(',')[0]
            try:
                last_num = int(last_id.replace(prefix, ""))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"
    except Exception as e:
        print("Error generating ID:", e)
        return None


# ====================== ADMINISTRATOR MENU ======================
def admin_menu():
    while True:
        print("\n===== ADMINISTRATOR MENU =====")
        print("1. Add Inventory Item")
        print("2. Remove Inventory Item")
        print("3. Update Inventory Item")
        print("4. View Low-Stock Warnings")
        print("5. Generate Overall Sales & Stock Report")
        print("6. Supplier Order Management")
        print("7. Exit to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_inventory_item()
        elif choice == "2":
            remove_inventory_item()
        elif choice == "3":
            update_inventory_item()
        elif choice == "4":
            low_stock_warning()
        elif choice == "5":
            generate_overall_sales_and_stock_report()
        elif choice == "6":
            manage_supplier_orders()
        elif choice == "7":
            print("Exiting administrator menu...")
            return
        else:
            print("Invalid choice. Try again.")


def load_inventory():
    """加载库存数据，与文档格式完全匹配"""
    inventory = []
    try:
        with open(INVENTORY_FILE, "r") as file:
            next(file)  # Skip header
            for line in file:
                item_data = line.strip().split(",")
                if len(item_data) >= 7:  # 确保有7个字段
                    try:
                        item = {
                            'item_id': item_data[0],
                            'item_name': item_data[1],
                            'category': item_data[2],
                            'price': float(item_data[3]),
                            'stock': int(item_data[4]),
                            'supplier_id': item_data[5],
                            'low_stock_level': int(item_data[6])
                        }
                        inventory.append(item)
                    except ValueError:
                        print(f"Warning: Skipping invalid line: {line}")
                        continue
    except FileNotFoundError:
        print("Inventory file not found. Creating a new one...")
        # 创建带有正确标题的新文件
        with open(INVENTORY_FILE, "w") as file:
            file.write("item_id,item_name,category,price,stock,supplier_id,low_stock_level\n")
    return inventory


def save_inventory(inventory):
    """保存库存数据，保持与文档相同的格式"""
    with open(INVENTORY_FILE, "w") as file:
        file.write("item_id,item_name,category,price,stock,supplier_id,low_stock_level\n")
        for item in inventory:
            file.write(f"{item['item_id']},{item['item_name']},{item['category']},"
                       f"{item['price']},{item['stock']},{item['supplier_id']},"
                       f"{item['low_stock_level']}\n")


def generate_unique_id(prefix, filename):
    """生成唯一ID"""
    try:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            with open(filename, 'w') as f:
                f.write("")
            lines = []

        if lines:
            last_id = lines[-1].split(',')[0]
            try:
                last_num = int(last_id.replace(prefix, ""))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"
    except Exception as e:
        print("Error generating ID:", e)
        return None


def get_current_date():
    """获取当前日期"""
    return input("Enter current date (YYYY-MM-DD): ")


def add_inventory_item():
    print("\n===== ADD INVENTORY ITEM =====")

    # 加载现有库存
    inventory = load_inventory()

    # 生成唯一的商品ID
    item_id = generate_unique_id("ITM", INVENTORY_FILE)

    # 获取商品名称（带查重验证）
    while True:
        item_name = input("Enter item name: ").strip()
        if not item_name:
            print("Item name cannot be empty.")
            continue

        # 检查名称是否重复（不区分大小写）
        name_exists = False
        for item in inventory:
            if item['item_name'].lower() == item_name.lower():
                name_exists = True
                print(f"Error: Item name '{item_name}' already exists in inventory.")
                print("Please choose a different name.")
                break

        if not name_exists:
            break

    # 获取其他信息
    category = input("Enter category: ").strip()

    # 验证价格
    while True:
        price_input = input("Enter item price: ")
        try:
            price = float(price_input)
            if price <= 0:
                print("Price must be positive.")
                continue
            break
        except ValueError:
            print("Invalid price. Please enter a number.")

    # 验证库存
    while True:
        stock_input = input("Enter stock quantity: ")
        try:
            stock = int(stock_input)
            if stock < 0:
                print("Stock cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid quantity. Please enter a whole number.")

    supplier_id = input("Enter supplier ID: ").strip()

    # 验证低库存水平
    while True:
        low_stock_input = input("Enter low stock level: ")
        try:
            low_stock_level = int(low_stock_input)
            if low_stock_level < 0:
                print("Low stock level cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid value. Please enter a whole number.")

    # 创建新商品
    new_item = {
        'item_id': item_id,
        'item_name': item_name,
        'category': category,
        'price': price,
        'stock': stock,
        'supplier_id': supplier_id,
        'low_stock_level': low_stock_level
    }

    # 添加到库存
    inventory.append(new_item)
    save_inventory(inventory)
    print(f"\nItem '{item_name}' added successfully! Item ID: {item_id}")


def remove_inventory_item():
    print("\n===== REMOVE INVENTORY ITEM =====")
    inventory = load_inventory()

    if not inventory:
        print("Inventory is empty.")
        return

    # 显示当前库存
    print("Current Inventory:")
    for item in inventory:
        print(f"{item['item_id']} - {item['item_name']} | Stock: {item['stock']} | Category: {item['category']}")

    item_id = input("\nEnter item ID to remove: ")

    found = False
    updated_inventory = []
    for item in inventory:
        if item['item_id'] == item_id:
            found = True
            confirm = input(f"Are you sure you want to remove {item['item_name']}? (y/n): ").lower()
            if confirm == 'y':
                print(f"Removed item: {item['item_name']}")
                continue  # 跳过这个项目，不添加到更新后的库存
            else:
                print("Removal cancelled.")
                updated_inventory.append(item)
        else:
            updated_inventory.append(item)

    if not found:
        print("Item not found.")
        return

    save_inventory(updated_inventory)
    print("Inventory updated successfully.")


def update_inventory_item():
    print("\n===== UPDATE INVENTORY ITEM =====")
    inventory = load_inventory()

    if not inventory:
        print("Inventory is empty.")
        return

    # 显示当前库存
    print("Current Inventory:")
    for item in inventory:
        print(f"{item['item_id']} - {item['item_name']} | Stock: {item['stock']} | Price: {item['price']}")

    item_id = input("\nEnter item ID to update: ")

    found = False
    for i, item in enumerate(inventory):
        if item['item_id'] == item_id:
            found = True
            print(f"\nUpdating item: {item['item_name']}")
            print("1. Update item name")
            print("2. Update category")
            print("3. Update price")
            print("4. Update stock quantity")
            print("5. Update supplier ID")
            print("6. Update low stock level")

            choice = input("Enter your choice: ")

            if choice == "1":
                new_name = input("Enter new item name: ")
                inventory[i]['item_name'] = new_name
                print("Item name updated.")
            elif choice == "2":
                new_category = input("Enter new category: ")
                inventory[i]['category'] = new_category
                print("Category updated.")
            elif choice == "3":
                while True:
                    new_price = input("Enter new price: ")
                    try:
                        price = float(new_price)
                        if price <= 0:
                            print("Price must be positive.")
                            continue
                        inventory[i]['price'] = price
                        print("Price updated.")
                        break
                    except ValueError:
                        print("Invalid price. Please enter a number.")
            elif choice == "4":
                while True:
                    new_stock = input("Enter new stock quantity: ")
                    try:
                        stock = int(new_stock)
                        if stock < 0:
                            print("Stock cannot be negative.")
                            continue
                        inventory[i]['stock'] = stock
                        print("Stock updated.")
                        break
                    except ValueError:
                        print("Invalid quantity. Please enter a whole number.")
            elif choice == "5":
                new_supplier = input("Enter new supplier ID: ")
                inventory[i]['supplier_id'] = new_supplier
                print("Supplier ID updated.")
            elif choice == "6":
                while True:
                    new_low_stock = input("Enter new low stock level: ")
                    try:
                        low_stock = int(new_low_stock)
                        if low_stock < 0:
                            print("Low stock level cannot be negative.")
                            continue
                        inventory[i]['low_stock_level'] = low_stock
                        print("Low stock level updated.")
                        break
                    except ValueError:
                        print("Invalid value. Please enter a whole number.")
            else:
                print("Invalid choice.")
                return

            save_inventory(inventory)
            print("Inventory updated successfully.")
            break

    if not found:
        print("Item not found.")


def low_stock_warning():
    print("\n===== LOW STOCK WARNINGS =====")
    inventory = load_inventory()

    if not inventory:
        print("Inventory is empty.")
        return

    low_stock_items = []
    for item in inventory:
        if item['stock'] <= item['low_stock_level']:
            low_stock_items.append(item)

    if not low_stock_items:
        print("No low stock items found.")
    else:
        print(f"{'Item ID':<10} {'Item Name':<20} {'Category':<15} {'Stock':<8} {'Low Level':<10} {'Supplier':<10}")
        print("-" * 85)
        for item in low_stock_items:
            print(f"{item['item_id']:<10} {item['item_name']:<20} {item['category']:<15} "
                  f"{item['stock']:<8} {item['low_stock_level']:<10} {item['supplier_id']:<10}")


def generate_overall_sales_and_stock_report():
    print("\n===== OVERALL SALES & STOCK REPORT =====")
    inventory = load_inventory()

    if not inventory:
        print("Inventory is empty.")
        return

    # 读取销售数据
    try:
        with open(SALES_FILE, 'r') as f:
            sales_lines = f.readlines()
    except FileNotFoundError:
        print("Sales file not found. Creating empty file...")
        with open(SALES_FILE, 'w') as f:
            f.write("sale_id,item_id,quantity,total_amount,date\n")
        sales_lines = []

    # 统计销售数据
    sales_by_item = {}
    total_sales_revenue = 0.0

    for line in sales_lines[1:]:  # 跳过标题行
        data = line.strip().split(',')
        if len(data) >= 5:
            item_id = data[1]
            quantity = int(data[2])
            amount = float(data[3])

            if item_id not in sales_by_item:
                sales_by_item[item_id] = {'quantity': 0, 'amount': 0.0}

            sales_by_item[item_id]['quantity'] += quantity
            sales_by_item[item_id]['amount'] += amount
            total_sales_revenue += amount

    # 生成报告
    print(f"{'Item ID':<10} {'Item Name':<20} {'Category':<15} {'Price':<8} "
          f"{'Stock':<8} {'Sold Qty':<10} {'Sales Amt':<12}")
    print("-" * 95)

    for item in inventory:
        item_id = item['item_id']
        sales_info = sales_by_item.get(item_id, {'quantity': 0, 'amount': 0.0})

        print(f"{item['item_id']:<10} {item['item_name']:<20} {item['category']:<15} "
              f"{item['price']:<8.2f} {item['stock']:<8} "
              f"{sales_info['quantity']:<10} {sales_info['amount']:<12.2f}")

    print("-" * 95)
    print(f"Total Sales Revenue: ${total_sales_revenue:.2f}")
    print(f"Total Items in Inventory: {len(inventory)}")

    # 保存报告到文件
    report_date = get_current_date()
    report_filename = f"sales_stock_report_{report_date.replace('-', '')}.txt"

    with open(report_filename, 'w') as f:
        f.write("Overall Sales & Stock Report\n")
        f.write(f"Date: {report_date}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Item ID':<10} {'Item Name':<20} {'Category':<15} {'Price':<8} "
                f"{'Stock':<8} {'Sold Qty':<10} {'Sales Amt':<12}\n")
        f.write("-" * 95 + "\n")

        for item in inventory:
            item_id = item['item_id']
            sales_info = sales_by_item.get(item_id, {'quantity': 0, 'amount': 0.0})

            f.write(f"{item['item_id']:<10} {item['item_name']:<20} {item['category']:<15} "
                    f"{item['price']:<8.2f} {item['stock']:<8} "
                    f"{sales_info['quantity']:<10} {sales_info['amount']:<12.2f}\n")

        f.write("-" * 95 + "\n")
        f.write(f"Total Sales Revenue: ${total_sales_revenue:.2f}\n")
        f.write(f"Total Items in Inventory: {len(inventory)}\n")

    print(f"\nReport saved to: {report_filename}")


def manage_supplier_orders():
    print("\n===== SUPPLIER ORDER MANAGEMENT =====")
    print("1. View All Suppliers")
    print("2. Add New Supplier Order")
    print("3. View Pending Orders")
    print("4. Update Order Status")

    choice = input("Enter your choice: ")

    if choice == "1":
        view_all_suppliers()
    elif choice == "2":
        add_supplier_order()
    elif choice == "3":
        view_pending_orders_admin()
    elif choice == "4":
        update_order_status_admin()
    else:
        print("Invalid choice.")


def view_all_suppliers():
    print("\n===== ALL SUPPLIERS =====")
    try:
        with open(SUPPLIER_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) <= 1:
                print("No suppliers found.")
                return

            print(f"{'Supplier ID':<12} {'Supplier Name':<20} {'Contact':<15} {'Email':<20} {'Balance':<10}")
            print("-" * 85)

            for line in lines[1:]:
                data = line.strip().split(',')
                if len(data) >= 6:
                    balance = float(data[5]) if len(data) > 5 and data[5] else 0.0
                    print(f"{data[0]:<12} {data[1]:<20} {data[2]:<15} {data[3]:<20} {balance:<10.2f}")
    except FileNotFoundError:
        print("Supplier file not found.")


def add_supplier_order():
    print("\n===== ADD SUPPLIER ORDER =====")
    order_id = generate_unique_id("ORD", ORDERS_FILE)

    supplier_id = input("Enter supplier ID: ")
    order_details = input("Enter order details: ")

    # 默认状态
    delivery_status = "Pending"
    payment_status = "Unpaid"

    new_order = f"{order_id},{supplier_id},{order_details},{delivery_status},{payment_status}\n"

    try:
        with open(ORDERS_FILE, 'a') as f:
            f.write(new_order)
        print(f"Order added successfully! Order ID: {order_id}")
    except Exception as e:
        print(f"Error adding order: {e}")


def view_pending_orders_admin():
    print("\n===== PENDING ORDERS =====")
    try:
        with open(ORDERS_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) <= 1:
                print("No orders found.")
                return

            print(f"{'Order ID':<10} {'Supplier ID':<12} {'Order Details':<30} {'Delivery':<10} {'Payment':<10}")
            print("-" * 75)

            pending_found = False
            for line in lines[1:]:
                data = line.strip().split(',')
                if len(data) >= 5:
                    if data[3] == "Pending" or data[4] == "Unpaid":
                        pending_found = True
                        order_details = data[2] if len(data) > 2 else ""
                        if len(order_details) > 30:
                            order_details = order_details[:27] + "..."
                        print(f"{data[0]:<10} {data[1]:<12} {order_details:<30} {data[3]:<10} {data[4]:<10}")

            if not pending_found:
                print("No pending orders found.")
    except FileNotFoundError:
        print("Orders file not found.")


def update_order_status_admin():
    print("\n===== UPDATE ORDER STATUS =====")
    order_id = input("Enter order ID to update: ")

    try:
        with open(ORDERS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No orders found.")
            return

        order_found = False
        updated_lines = [lines[0]]  # 保持标题行

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 5 and data[0] == order_id:
                order_found = True
                print(f"Current status: Delivery={data[3]}, Payment={data[4]}")
                print("Select status to update:")
                print("1. Mark as Delivered")
                print("2. Mark as Paid")
                print("3. Mark as Delivered and Paid")

                choice = input("Enter your choice: ")

                if choice == "1":
                    data[3] = "Delivered"
                elif choice == "2":
                    data[4] = "Paid"
                elif choice == "3":
                    data[3] = "Delivered"
                    data[4] = "Paid"
                else:
                    print("Invalid choice. No changes made.")

                line = ','.join(data) + '\n'

            updated_lines.append(line)

        if order_found:
            with open(ORDERS_FILE, 'w') as f:
                f.writelines(updated_lines)
            print("Order status updated successfully.")
        else:
            print("Order not found.")
    except FileNotFoundError:
        print("Orders file not found.")


# ====================== CASHIER MENU ======================
def cashier_menu():
    while True:
        print("\n========== CASHIER MENU ==========")
        print("1. Process Sale")
        print("2. Refund/Return Item")
        print("3. Exit to Main Menu")
        print("==================================")

        choice = input("Enter choice: ")

        if choice == "1":
            process_sale()
        elif choice == "2":
            refund_item()
        elif choice == "3":
            print("Exiting Cashier Module...")
            return
        else:
            print("Invalid choice! Please try again.")


def process_sale():
    inventory = load_inventory()

    print("\n====== PROCESS SALES ======")
    item_id = input("Enter Item ID: ")

    item_found = None
    for item in inventory:
        if item['item_id'] == item_id:
            item_found = item
            break

    if item_found is None:
        print("Item not found!")
        return

    print(f"Item: {item_found['item_name']}")
    print(f"Price: RM {item_found['price']:.2f}")
    print(f"Available Stock: {item_found['stock']}")

    while True:
        qty_input = input("Enter quantity: ")
        try:
            qty = int(qty_input)
            if qty <= 0:
                print("Quantity must be positive!")
                continue
            if qty > item_found['stock']:
                print("Not enough stock available!")
                return
            break
        except ValueError:
            print("Invalid quantity! Please enter a number.")

    total = qty * item_found['price']
    print(f"Total Price: RM {total:.2f}")

    confirm = input("Confirm purchase? (y/n): ").lower()
    if confirm != "y":
        print("Sale Cancelled.")
        return

    item_found['stock'] -= qty
    save_inventory(inventory)

    sale_id = generate_unique_id("SAL", SALES_FILE)
    date = get_current_date()
    with open(SALES_FILE, "a") as file:
        file.write(f"{sale_id},{item_id},{qty},{total:.2f},{date}\n")

    print("\n===== RECEIPT =====")
    print(f"Sale ID: {sale_id}")
    print(f"Date: {date}")
    print(f"Item: {item_found['item_name']}")
    print(f"Qty: {qty}")
    print(f"Total: RM {total:.2f}")
    print("===================\n")


def refund_item():
    inventory = load_inventory()

    print("\n====== REFUND / RETURN ======")
    item_id = input("Enter Item ID for Refund: ")

    while True:
        qty_input = input("Enter Quantity to Return: ")
        try:
            qty = int(qty_input)
            if qty <= 0:
                print("Quantity must be positive!")
                continue
            break
        except ValueError:
            print("Invalid quantity! Only numbers allowed.")

    item_found = None
    for item in inventory:
        if item['item_id'] == item_id:
            item_found = item
            break

    if item_found is None:
        print("Item ID not found!")
        return

    item_found['stock'] += qty
    save_inventory(inventory)

    refund_amount = qty * item_found['price']
    refund_id = generate_unique_id("REF", REFUNDS_FILE)
    date = get_current_date()

    with open(REFUNDS_FILE, "a") as file:
        file.write(f"{refund_id},{item_id},{qty},{refund_amount:.2f},{date}\n")

    print("\n===== REFUND RECEIPT =====")
    print(f"Refund ID: {refund_id}")
    print(f"Date: {date}")
    print(f"Item: {item_found['item_name']}")
    print(f"Qty Returned: {qty}")
    print(f"Refund Amount: RM {refund_amount:.2f}")
    print("===========================\n")


# ====================== ACCOUNTANT MENU ======================
def accountant_menu():
    """会计主菜单"""
    while True:
        print("\n===== ACCOUNTANT MENU =====")
        print("1. Record Payments")
        print("2. Generate Financial Reports")
        print("3. Track Unpaid Balances")
        print("4. View All Payments")
        print("5. Exit to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            record_payments_menu()
        elif choice == "2":
            generate_report_menu()
        elif choice == "3":
            track_unpaid_balances_menu()
        elif choice == "4":
            view_all_payments()
        elif choice == "5":
            print("Exiting Accountant Menu...")
            return
        else:
            print("Invalid choice. Try again.")

def generate_daily_report():
    """生成日报 - 先展示后保存"""
    date = input("Enter date for daily report (YYYY-MM-DD): ").strip()

    if not date:
        print("Date cannot be empty.")
        return

    # 收入统计
    daily_income = 0.0
    income_records = []
    try:
        with open(PAYMENTS_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 7 and data[1] == date and data[5] == "Paid" and data[2] == "Customer":
                    try:
                        amount = float(data[4])
                        daily_income += amount
                        income_records.append({
                            'id': data[0],
                            'customer_id': data[3],
                            'amount': amount,
                            'status': data[5],
                            'remarks': data[6] if len(data) > 6 else ""
                        })
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Payments file not found.")

    # 支出统计
    daily_expense = 0.0
    expense_records = []
    try:
        with open(PAYMENTS_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 7 and data[1] == date and data[5] == "Paid" and data[2] == "Supplier":
                    try:
                        amount = float(data[4])
                        daily_expense += amount
                        expense_records.append({
                            'id': data[0],
                            'supplier_id': data[3],
                            'amount': amount,
                            'status': data[5],
                            'remarks': data[6] if len(data) > 6 else ""
                        })
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Payments file not found.")

    # 计算净现金流
    net_cash_flow = daily_income - daily_expense

    # 生成报告内容
    report_id = generate_unique_id("DR", "daily_reports")

    content = f"Daily Financial Report - {date}\n"
    content += f"Report ID: {report_id}\n"
    content += "=" * 50 + "\n\n"
    content += f"Total Income: ${daily_income:.2f}\n"
    content += f"Total Expenses: ${daily_expense:.2f}\n"
    content += f"Net Cash Flow: ${net_cash_flow:.2f}\n\n"

    content += "Income Details (Customer Payments - Paid):\n"
    for record in income_records:
        content += f"  {record['id']}: Customer {record['customer_id']} - ${record['amount']:.2f} ({record['remarks']})\n"

    content += "\nExpense Details (Supplier Payments - Paid):\n"
    for record in expense_records:
        content += f"  {record['id']}: Supplier {record['supplier_id']} - ${record['amount']:.2f} ({record['remarks']})\n"

    # 先展示报告
    print("\n" + "=" * 60)
    print("DAILY FINANCIAL REPORT - PREVIEW")
    print("=" * 60)
    print(content)

    # 询问是否保存
    save_choice = input("Save this report to file? (y/n): ").lower().strip()
    if save_choice == 'y':
        filename = f"daily_report_{date.replace('-', '')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"Daily report saved: {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")
    else:
        print("Report not saved.")

def generate_monthly_report():
    """生成月报 - 先展示后保存"""
    month = input("Enter month for report (YYYY-MM): ").strip()

    if not month or len(month) != 7:
        print("Invalid month format. Use YYYY-MM.")
        return

    # 收入统计
    monthly_income = 0.0
    income_by_day = {}
    try:
        with open(PAYMENTS_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 7 and data[1].startswith(month) and data[5] == "Paid" and data[2] == "Customer":
                    try:
                        amount = float(data[4])
                        monthly_income += amount

                        # 按日期分组
                        date = data[1]
                        if date not in income_by_day:
                            income_by_day[date] = 0.0
                        income_by_day[date] += amount
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Payments file not found.")

    # 支出统计
    monthly_expense = 0.0
    expense_by_day = {}
    try:
        with open(PAYMENTS_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 7 and data[1].startswith(month) and data[5] == "Paid" and data[2] == "Supplier":
                    try:
                        amount = float(data[4])
                        monthly_expense += amount

                        # 按日期分组
                        date = data[1]
                        if date not in expense_by_day:
                            expense_by_day[date] = 0.0
                        expense_by_day[date] += amount
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Payments file not found.")

    # 计算净现金流
    net_cash_flow = monthly_income - monthly_expense

    # 生成报告内容
    report_id = generate_unique_id("MR", "monthly_reports")

    content = f"Monthly Financial Report - {month}\n"
    content += f"Report ID: {report_id}\n"
    content += "=" * 50 + "\n\n"
    content += f"Total Monthly Income: ${monthly_income:.2f}\n"
    content += f"Total Monthly Expenses: ${monthly_expense:.2f}\n"
    content += f"Net Cash Flow: ${net_cash_flow:.2f}\n\n"

    content += "Daily Income Breakdown:\n"
    for date, amount in sorted(income_by_day.items()):
        content += f"  {date}: ${amount:.2f}\n"

    content += "\nDaily Expense Breakdown:\n"
    for date, amount in sorted(expense_by_day.items()):
        content += f"  {date}: ${amount:.2f}\n"

    # 先展示报告
    print("\n" + "=" * 60)
    print("MONTHLY FINANCIAL REPORT - PREVIEW")
    print("=" * 60)
    print(content)

    # 询问是否保存
    save_choice = input("Save this report to file? (y/n): ").lower().strip()
    if save_choice == 'y':
        filename = f"monthly_report_{month.replace('-', '')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"Monthly report saved: {filename}")
        except Exception as e:
            print(f"Error saving report: {e}")
    else:
        print("Report not saved.")

def track_unpaid_balances_menu():
    """跟踪未付余额子菜单 - 基于Payments文件"""
    while True:
        print("\n===== UNPAID BALANCES =====")
        print("1. View All Unpaid Suppliers")
        print("2. View All Unpaid Customers")
        print("3. Search Unpaid Supplier")
        print("4. Search Unpaid Customer")
        print("5. View High Unpaid Suppliers (>1000)")
        print("6. View High Unpaid Customers (>500)")
        print("7. Back to Accountant Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            view_unpaid_suppliers()
        elif choice == "2":
            view_unpaid_customers()
        elif choice == "3":
            search_unpaid_supplier()
        elif choice == "4":
            search_unpaid_customer()
        elif choice == "5":
            view_high_unpaid_suppliers()
        elif choice == "6":
            view_high_unpaid_customers()
        elif choice == "7":
            return
        else:
            print("Invalid choice. Try again.")

def update_supplier_balance(supplier_id, amount, status):
    """更新供应商余额"""
    try:
        with open(SUPPLIER_FILE, 'r') as f:
            lines = f.readlines()

        updated_lines = []
        header = lines[0]
        updated_lines.append(header)

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 6 and data[0] == supplier_id:
                try:
                    current_balance = float(data[5])
                    if status == "Paid":
                        new_balance = current_balance - amount
                    else:  # Unpaid
                        new_balance = current_balance + amount

                    # 确保余额不为负
                    if new_balance < 0:
                        new_balance = 0.0

                    data[5] = f"{new_balance:.2f}"
                    updated_line = ','.join(data) + '\n'
                    updated_lines.append(updated_line)
                    print(f"Supplier balance updated: {current_balance:.2f} -> {new_balance:.2f}")
                except ValueError:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        with open(SUPPLIER_FILE, 'w') as f:
            f.writelines(updated_lines)

    except Exception as e:
        print(f"Error updating supplier balance: {e}")

def update_customer_balance(customer_id, amount, status):
    """更新客户余额（删除地址列）"""
    try:
        with open(CUSTOMER_FILE, 'r') as f:
            lines = f.readlines()

        updated_lines = []
        header = lines[0]
        updated_lines.append(header)

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 5 and data[0] == customer_id:  # 字段数量改为5
                try:
                    current_balance = float(data[4])  # 余额在索引4位置
                    if status == "Paid":
                        new_balance = current_balance - amount
                    else:  # Unpaid
                        new_balance = current_balance + amount

                    # 确保余额不为负
                    if new_balance < 0:
                        new_balance = 0.0

                    data[4] = f"{new_balance:.2f}"
                    updated_line = ','.join(data) + '\n'
                    updated_lines.append(updated_line)
                    print(f"Customer balance updated: {current_balance:.2f} -> {new_balance:.2f}")
                except ValueError:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        with open(CUSTOMER_FILE, 'w') as f:
            f.writelines(updated_lines)

    except Exception as e:
        print(f"Error updating customer balance: {e}")

def get_supplier_balance(supplier_id):
    """获取供应商余额"""
    try:
        with open(SUPPLIER_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 6 and data[0] == supplier_id:
                    try:
                        return float(data[5])
                    except ValueError:
                        return 0.0
    except FileNotFoundError:
        return 0.0
    return 0.0

def get_customer_balance(customer_id):
    """获取客户余额（删除地址列）"""
    try:
        with open(CUSTOMER_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 5 and data[0] == customer_id:  # 字段数量改为5
                    try:
                        return float(data[4])  # 余额在索引4位置
                    except ValueError:
                        return 0.0
    except FileNotFoundError:
        return 0.0
    return 0.0

def view_unpaid_suppliers():
    """查看所有未付供应商 - 基于Payments文件动态计算"""
    print("\n===== UNPAID SUPPLIERS =====")

    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        # 使用字典按供应商ID分组计算未付总额
        unpaid_suppliers = {}

        for line in lines[1:]:  # 跳过标题行
            data = line.strip().split(',')
            if len(data) >= 6:
                payer_type = data[2]
                status = data[5]
                if payer_type == "Supplier" and status == "Unpaid":
                    supplier_id = data[3]
                    try:
                        amount = float(data[4])
                        if supplier_id not in unpaid_suppliers:
                            unpaid_suppliers[supplier_id] = 0.0
                        unpaid_suppliers[supplier_id] += amount
                    except ValueError:
                        continue

        if not unpaid_suppliers:
            print("No unpaid suppliers found.")
            return

        # 获取供应商名称（从供应商文件）
        supplier_names = {}
        try:
            with open(SUPPLIER_FILE, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    s_data = line.strip().split(',')
                    if len(s_data) >= 2:
                        supplier_id = s_data[0]
                        supplier_name = s_data[1]
                        supplier_names[supplier_id] = supplier_name
        except FileNotFoundError:
            print("Supplier file not found. Will display IDs only.")

        # 显示结果
        header = "Supplier ID,Supplier Name,Unpaid Amount"
        print(header)
        print("-" * len(header))

        total_unpaid = 0.0
        for supplier_id, amount in unpaid_suppliers.items():
            supplier_name = supplier_names.get(supplier_id, "Unknown")
            print(f"{supplier_id},{supplier_name},{amount:.2f}")
            total_unpaid += amount

        print(f"\nTotal Unpaid Suppliers: {len(unpaid_suppliers)}")
        print(f"Total Unpaid Amount: ${total_unpaid:.2f}")

    except FileNotFoundError:
        print("Payments file not found.")

def view_unpaid_customers():
    """查看所有未付客户 - 基于Payments文件动态计算"""
    print("\n===== UNPAID CUSTOMERS =====")

    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        # 使用字典按客户ID分组计算未付总额
        unpaid_customers = {}

        for line in lines[1:]:  # 跳过标题行
            data = line.strip().split(',')
            if len(data) >= 6:
                payer_type = data[2]
                status = data[5]
                if payer_type == "Customer" and status == "Unpaid":
                    customer_id = data[3]
                    try:
                        amount = float(data[4])
                        if customer_id not in unpaid_customers:
                            unpaid_customers[customer_id] = 0.0
                        unpaid_customers[customer_id] += amount
                    except ValueError:
                        continue

        if not unpaid_customers:
            print("No unpaid customers found.")
            return

        # 获取客户名称（从客户文件）
        customer_names = {}
        try:
            with open(CUSTOMER_FILE, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    c_data = line.strip().split(',')
                    if len(c_data) >= 2:
                        customer_id = c_data[0]
                        customer_name = c_data[1]
                        customer_names[customer_id] = customer_name
        except FileNotFoundError:
            print("Customer file not found. Will display IDs only.")

        # 显示结果
        header = "Customer ID,Customer Name,Unpaid Amount"
        print(header)
        print("-" * len(header))

        total_unpaid = 0.0
        for customer_id, amount in unpaid_customers.items():
            customer_name = customer_names.get(customer_id, "Unknown")
            print(f"{customer_id},{customer_name},{amount:.2f}")
            total_unpaid += amount

        print(f"\nTotal Unpaid Customers: {len(unpaid_customers)}")
        print(f"Total Unpaid Amount: ${total_unpaid:.2f}")

    except FileNotFoundError:
        print("Payments file not found.")

def search_unpaid_supplier():
    """搜索未付供应商 - 基于Payments文件"""
    supplier_id = input("Enter Supplier ID to search: ").strip().upper()

    if not supplier_id:
        print("Supplier ID cannot be empty.")
        return

    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        unpaid_amount = 0.0
        unpaid_records = []

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 6:
                payer_type = data[2]
                status = data[5]
                if (payer_type == "Supplier" and status == "Unpaid" and
                        data[3] == supplier_id):
                    try:
                        amount = float(data[4])
                        unpaid_amount += amount
                        unpaid_records.append({
                            'payment_id': data[0],
                            'date': data[1],
                            'amount': amount,
                            'remarks': data[6] if len(data) > 6 else ""
                        })
                    except ValueError:
                        continue

        if unpaid_amount > 0:
            # 获取供应商名称
            supplier_name = "Unknown"
            try:
                with open(SUPPLIER_FILE, 'r') as f:
                    next(f)  # Skip header
                    for line in f:
                        s_data = line.strip().split(',')
                        if len(s_data) >= 2 and s_data[0] == supplier_id:
                            supplier_name = s_data[1]
                            break
            except FileNotFoundError:
                pass

            print(f"\nSupplier Details:")
            print(f"  ID: {supplier_id}")
            print(f"  Name: {supplier_name}")
            print(f"  Total Unpaid Amount: ${unpaid_amount:.2f}")
            print(f"  Status: UNPAID")
            print(f"  Unpaid Records: {len(unpaid_records)}")

            for record in unpaid_records:
                print(
                    f"    - {record['payment_id']} on {record['date']}: ${record['amount']:.2f} ({record['remarks']})")
        else:
            print(f"No unpaid records found for supplier {supplier_id}.")

    except FileNotFoundError:
        print("Payments file not found.")

def search_unpaid_customer():
    """搜索未付客户 - 基于Payments文件"""
    customer_id = input("Enter Customer ID to search: ").strip().upper()

    if not customer_id:
        print("Customer ID cannot be empty.")
        return

    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        unpaid_amount = 0.0
        unpaid_records = []

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 6:
                payer_type = data[2]
                status = data[5]
                if (payer_type == "Customer" and status == "Unpaid" and
                        data[3] == customer_id):
                    try:
                        amount = float(data[4])
                        unpaid_amount += amount
                        unpaid_records.append({
                            'payment_id': data[0],
                            'date': data[1],
                            'amount': amount,
                            'remarks': data[6] if len(data) > 6 else ""
                        })
                    except ValueError:
                        continue

        if unpaid_amount > 0:
            # 获取客户名称
            customer_name = "Unknown"
            try:
                with open(CUSTOMER_FILE, 'r') as f:
                    next(f)  # Skip header
                    for line in f:
                        c_data = line.strip().split(',')
                        if len(c_data) >= 2 and c_data[0] == customer_id:
                            customer_name = c_data[1]
                            break
            except FileNotFoundError:
                pass

            print(f"\nCustomer Details:")
            print(f"  ID: {customer_id}")
            print(f"  Name: {customer_name}")
            print(f"  Total Unpaid Amount: ${unpaid_amount:.2f}")
            print(f"  Status: UNPAID")
            print(f"  Unpaid Records: {len(unpaid_records)}")

            for record in unpaid_records:
                print(
                    f"    - {record['payment_id']} on {record['date']}: ${record['amount']:.2f} ({record['remarks']})")
        else:
            print(f"No unpaid records found for customer {customer_id}.")

    except FileNotFoundError:
        print("Payments file not found.")

def view_high_unpaid_suppliers():
    """查看高未付余额供应商 (>1000) - 基于Payments文件"""
    print("\n===== HIGH UNPAID SUPPLIERS (>1000) =====")

    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        # 计算每个供应商的未付总额
        supplier_totals = {}

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 6:
                payer_type = data[2]
                status = data[5]
                if payer_type == "Supplier" and status == "Unpaid":
                    supplier_id = data[3]
                    try:
                        amount = float(data[4])
                        if supplier_id not in supplier_totals:
                            supplier_totals[supplier_id] = 0.0
                        supplier_totals[supplier_id] += amount
                    except ValueError:
                        continue

        # 筛选高余额供应商
        high_unpaid_suppliers = {sid: amt for sid, amt in supplier_totals.items() if amt > 1000}

        if not high_unpaid_suppliers:
            print("No suppliers with unpaid amount over $1000.")
            return

        # 获取供应商名称
        supplier_names = {}
        try:
            with open(SUPPLIER_FILE, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    s_data = line.strip().split(',')
                    if len(s_data) >= 2:
                        supplier_id = s_data[0]
                        supplier_name = s_data[1]
                        supplier_names[supplier_id] = supplier_name
        except FileNotFoundError:
            pass

        # 显示结果
        header = "Supplier ID,Supplier Name,Unpaid Amount"
        print(header)
        print("-" * len(header))

        for supplier_id, amount in high_unpaid_suppliers.items():
            supplier_name = supplier_names.get(supplier_id, "Unknown")
            print(f"{supplier_id},{supplier_name},{amount:.2f}")

        print(f"\nTotal High Unpaid Suppliers: {len(high_unpaid_suppliers)}")

    except FileNotFoundError:
        print("Payments file not found.")

def view_high_unpaid_customers():
    """查看高未付余额客户 (>500) - 基于Payments文件"""
    print("\n===== HIGH UNPAID CUSTOMERS (>500) =====")

    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        # 计算每个客户的未付总额
        customer_totals = {}

        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 6:
                payer_type = data[2]
                status = data[5]
                if payer_type == "Customer" and status == "Unpaid":
                    customer_id = data[3]
                    try:
                        amount = float(data[4])
                        if customer_id not in customer_totals:
                            customer_totals[customer_id] = 0.0
                        customer_totals[customer_id] += amount
                    except ValueError:
                        continue

        # 筛选高余额客户
        high_unpaid_customers = {cid: amt for cid, amt in customer_totals.items() if amt > 500}

        if not high_unpaid_customers:
            print("No customers with unpaid amount over $500.")
            return

        # 获取客户名称
        customer_names = {}
        try:
            with open(CUSTOMER_FILE, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    c_data = line.strip().split(',')
                    if len(c_data) >= 2:
                        customer_id = c_data[0]
                        customer_name = c_data[1]
                        customer_names[customer_id] = customer_name
        except FileNotFoundError:
            pass

        # 显示结果
        header = "Customer ID,Customer Name,Unpaid Amount"
        print(header)
        print("-" * len(header))

        for customer_id, amount in high_unpaid_customers.items():
            customer_name = customer_names.get(customer_id, "Unknown")
            print(f"{customer_id},{customer_name},{amount:.2f}")

        print(f"\nTotal High Unpaid Customers: {len(high_unpaid_customers)}")

    except FileNotFoundError:
        print("Payments file not found.")


# 其他函数保持不变（record_payments_menu, generate_report_menu, view_all_payments等）
# 这些函数已经正确实现，不需要修改

def record_payments_menu():
    """记录支付子菜单"""
    while True:
        print("\n===== RECORD PAYMENTS =====")
        print("1. Record Supplier Payment")
        print("2. Record Customer Payment")
        print("3. Back to Accountant Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            record_supplier_payment()
        elif choice == "2":
            record_customer_payment()
        elif choice == "3":
            return
        else:
            print("Invalid choice. Try again.")

def record_supplier_payment():
    """记录供应商支付"""
    print("\n--- Record Supplier Payment ---")
    supplier_id = input("Enter Supplier ID: ").strip().upper()

    if not supplier_id:
        print("Supplier ID cannot be empty.")
        return

    # 检查供应商是否存在
    supplier_found = False
    supplier_name = ""
    current_balance = 0.0
    try:
        with open(SUPPLIER_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 6 and data[0] == supplier_id:
                    supplier_found = True
                    supplier_name = data[1]
                    try:
                        current_balance = float(data[5])
                    except ValueError:
                        current_balance = 0.0
                    break
    except FileNotFoundError:
        print("Supplier file not found.")
        return

    if not supplier_found:
        print(f"Supplier ID {supplier_id} not found.")
        return

    print(f"Supplier: {supplier_name}")
    print(f"Current Balance: ${current_balance:.2f}")

    # 输入金额
    while True:
        amount_input = input("Enter payment amount: ")
        try:
            amount = float(amount_input)
            if amount <= 0:
                print("Amount must be positive.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")

    # 输入状态
    while True:
        status = input("Enter payment status (Paid/Unpaid): ").strip().capitalize()
        if status in ["Paid", "Unpaid"]:
            break
        else:
            print("Status must be 'Paid' or 'Unpaid'.")

    remarks = input("Enter remarks: ").strip()
    date = get_current_date()

    # 生成支付记录
    payment_id = generate_unique_id("P", PAYMENTS_FILE)
    payer_type = "Supplier"

    new_record = f"{payment_id},{date},{payer_type},{supplier_id},{amount:.2f},{status},{remarks}\n"

    try:
        # 确保支付文件存在
        ensure_payments_file_exists()

        # 追加支付记录
        with open(PAYMENTS_FILE, 'a') as f:
            f.write(new_record)
        print(f"Supplier payment recorded successfully. Payment ID: {payment_id}")

        # 更新供应商余额
        update_supplier_balance(supplier_id, amount, status)

        # 显示更新后的余额
        updated_balance = get_supplier_balance(supplier_id)
        print(f"Updated Supplier Balance: ${updated_balance:.2f}")

    except Exception as e:
        print(f"Error saving payment: {e}")

def record_customer_payment():
    """记录客户支付"""
    print("\n--- Record Customer Payment ---")
    customer_id = input("Enter Customer ID (format CXXX): ").strip().upper()

    if not customer_id or not customer_id.startswith('C'):
        print("Customer ID must start with 'C' followed by numbers.")
        return

    # 检查客户是否存在
    customer_found = False
    customer_name = ""
    current_balance = 0.0

    try:
        # 确保客户文件格式正确
        ensure_customer_file_format()

        with open(CUSTOMER_FILE, 'r') as f:
            next(f)  # Skip header
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 5 and data[0] == customer_id:  # 字段数量改为5
                    customer_found = True
                    customer_name = data[1]
                    try:
                        current_balance = float(data[4])  # 余额在索引4位置
                    except ValueError:
                        current_balance = 0.0
                    break
    except FileNotFoundError:
        print("Customer file not found.")
        return

    if not customer_found:
        print(f"Customer ID {customer_id} not found. Creating new customer record.")
        customer_name = input("Enter customer name: ").strip()
        contact = input("Enter contact: ").strip()
        email = input("Enter email: ").strip()

        # 创建新客户记录（余额初始为0，没有地址）
        new_customer = f"{customer_id},{customer_name},{contact},{email},0.00\n"
        try:
            with open(CUSTOMER_FILE, 'a') as f:
                f.write(new_customer)
            print("New customer added successfully.")
            current_balance = 0.0
        except Exception as e:
            print(f"Error adding customer: {e}")
            return

    print(f"Customer: {customer_name}")
    print(f"Current Balance: ${current_balance:.2f}")

    # 输入金额
    while True:
        amount_input = input("Enter payment amount: ")
        try:
            amount = float(amount_input)
            if amount <= 0:
                print("Amount must be positive.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")

    # 输入状态
    while True:
        status = input("Enter payment status (Paid/Unpaid): ").strip().capitalize()
        if status in ["Paid", "Unpaid"]:
            break
        else:
            print("Status must be 'Paid' or 'Unpaid'.")

    remarks = input("Enter remarks: ").strip()
    date = get_current_date()

    # 生成支付记录
    payment_id = generate_unique_id("P", PAYMENTS_FILE)
    payer_type = "Customer"

    new_record = f"{payment_id},{date},{payer_type},{customer_id},{amount:.2f},{status},{remarks}\n"

    try:
        # 确保支付文件存在
        ensure_payments_file_exists()

        # 追加支付记录
        with open(PAYMENTS_FILE, 'a') as f:
            f.write(new_record)
        print(f"Customer payment recorded successfully. Payment ID: {payment_id}")

        # 更新客户余额
        update_customer_balance(customer_id, amount, status)

        # 显示更新后的余额
        updated_balance = get_customer_balance(customer_id)
        print(f"Updated Customer Balance: ${updated_balance:.2f}")

    except Exception as e:
        print(f"Error saving payment: {e}")

def ensure_payments_file_exists():
    """确保支付文件存在且有正确标题"""
    try:
        with open(PAYMENTS_FILE, 'r') as f:
            first_line = f.readline().strip()
            if not first_line:
                # 空文件，写入标题
                with open(PAYMENTS_FILE, 'w') as f_write:
                    f_write.write("payment_id,date,payer_type,payer_id,amount,status,remarks\n")
    except FileNotFoundError:
        # 文件不存在，创建新文件
        with open(PAYMENTS_FILE, 'w') as f:
            f.write("payment_id,date,payer_type,payer_id,amount,status,remarks\n")

def ensure_customer_file_format():
    """确保客户文件有正确的格式和标题（删除地址列）"""
    try:
        with open(CUSTOMER_FILE, 'r') as f:
            first_line = f.readline().strip()
            if not first_line:
                # 空文件，写入正确标题（无地址）
                with open(CUSTOMER_FILE, 'w') as f_write:
                    f_write.write("customer_id,customer_name,contact,email,outstanding_balance\n")
            elif "outstanding_balance" not in first_line:
                # 标题不正确，重写文件
                lines = f.readlines()
                new_lines = ["customer_id,customer_name,contact,email,outstanding_balance\n"]
                for line in lines:
                    data = line.strip().split(',')
                    if len(data) >= 4:
                        # 添加余额字段（如果不存在）
                        if len(data) < 5:
                            data.append("0.00")
                        # 删除地址列（索引4）
                        new_data = data[:4] + [data[4]]  # 保留前4个字段和余额
                        new_lines.append(','.join(new_data) + '\n')
                with open(CUSTOMER_FILE, 'w') as f_write:
                    f_write.writelines(new_lines)
    except FileNotFoundError:
        # 文件不存在，创建新文件（无地址）
        with open(CUSTOMER_FILE, 'w') as f:
            f.write("customer_id,customer_name,contact,email,outstanding_balance\n")

def generate_report_menu():
    """生成报告子菜单"""
    while True:
        print("\n===== FINANCIAL REPORTS =====")
        print("1. Generate Daily Report")
        print("2. Generate Monthly Report")
        print("3. Back to Accountant Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            generate_daily_report()
        elif choice == "2":
            generate_monthly_report()
        elif choice == "3":
            return
        else:
            print("Invalid choice. Try again.")

def view_all_payments():
    """查看所有支付记录"""
    print("\n===== ALL PAYMENTS =====")
    try:
        with open(PAYMENTS_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) <= 1:
            print("No payment records found.")
            return

        # 显示标题
        header = lines[0].strip()
        print(header)
        print("-" * len(header))

        # 显示所有记录
        count = 0
        for line in lines[1:]:
            data = line.strip().split(',')
            if len(data) >= 6:
                print(line.strip())
                count += 1

        print(f"\nTotal payment records: {count}")

    except FileNotFoundError:
        print("Payments file not found.")


# 其他辅助函数（record_supplier_payment, record_customer_payment等）保持不变
# 因为它们已经正确实现了支付记录功能

# ====================== STOCK MANAGER MENU ======================
def stock_manager_menu():
    while True:
        print("\n===== STOCK MANAGER MENU =====")
        print("1. View Inventory")
        print("2. Generate Restock Requests")
        print("3. Manage Supplier Details")
        print("4. Record New Stock Arrivals")
        print("5. Exit to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_inventory()
        elif choice == "2":
            generate_restock_requests()
        elif choice == "3":
            manage_supplier_details()
        elif choice == "4":
            record_new_arrivals()
        elif choice == "5":
            print("Exiting stock manager menu...")
            return
        else:
            print("Invalid choice. Try again.")


def display_inventory():
    inventory = load_inventory()
    print("\nCurrent Inventory:")
    if not inventory:
        print("No inventory items found.")
        return

    for item in inventory:
        print(f"{item['item_id']} - {item['item_name']} | Price: {item['price']:.2f} | Stock: {item['stock']}")


def generate_restock_requests():
    inventory = load_inventory()
    if not inventory:
        print("\nNo inventory items found.")
        return

    restock_list = []
    for item in inventory:
        low_level = item.get('low_stock_level', LOW_STOCK_LEVEL)
        if item['stock'] <= low_level:
            restock_list.append(item)

    if not restock_list:
        print("\nNo items need restocking.")
    else:
        print("\nRestock Request List:")
        for item in restock_list:
            print(
                f"{item['item_id']} - {item['item_name']} | Stock: {item['stock']} | Low Stock Level: {item.get('low_stock_level', LOW_STOCK_LEVEL)}")


def manage_supplier_details():
    suppliers = load_suppliers()

    while True:
        print("\n===== SUPPLIER MANAGEMENT =====")
        print("1. Display All Suppliers")
        print("2. Search Supplier")
        print("3. Update Supplier")
        print("4. Back to Stock Manager Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            display_suppliers(suppliers)
        elif choice == "2":
            supplier_id = input("Enter supplier ID: ")
            search_supplier(suppliers, supplier_id)
        elif choice == "3":
            supplier_id = input("Enter supplier ID: ")
            new_contact = input("Enter new contact: ")
            new_email = input("Enter new email: ")
            new_address = input("Enter new address: ")
            new_balance = input("Enter new outstanding balance: ")
            update_supplier(suppliers, supplier_id, new_contact, new_email, new_address, new_balance)
            save_suppliers(suppliers)
        elif choice == "4":
            break
        else:
            print("Invalid choice!")


def load_suppliers():
    suppliers = []
    try:
        with open(SUPPLIER_FILE, 'r') as file:
            next(file)
            for line in file:
                data = line.strip().split(',')
                if len(data) >= 6:
                    try:
                        supplier = {
                            'supplier_id': data[0],
                            'supplier_name': data[1],
                            'contact': data[2] if len(data) > 2 else "",
                            'email': data[3] if len(data) > 3 else "",
                            'address': data[4] if len(data) > 4 else "",
                            'outstanding_balance': float(data[5]) if len(data) > 5 and data[5] else 0.0
                        }
                        suppliers.append(supplier)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print("Supplier file not found. Creating empty list.")
    return suppliers


def save_suppliers(suppliers):
    with open(SUPPLIER_FILE, 'w') as file:
        file.write("supplier_id,supplier_name,contact,email,address,outstanding_balance\n")
        for supplier in suppliers:
            line = f"{supplier['supplier_id']},{supplier['supplier_name']},{supplier['contact']},{supplier['email']},{supplier['address']},{supplier['outstanding_balance']:.2f}\n"
            file.write(line)


def display_suppliers(suppliers):
    print("\nSupplier List:")
    for s in suppliers:
        print(
            f"{s['supplier_id']} - {s['supplier_name']} | Contact: {s['contact']} | Email: {s['email']} | Address: {s['address']} | Balance: {s['outstanding_balance']:.2f}")


def search_supplier(suppliers, supplier_id):
    for s in suppliers:
        if s["supplier_id"] == supplier_id:
            print(f"\nSupplier Found: {s['supplier_id']} - {s['supplier_name']}")
            print(
                f"Contact: {s['contact']}, Email: {s['email']}, Address: {s['address']}, Balance: {s['outstanding_balance']:.2f}")
            return
    print("Supplier not found.")


def update_supplier(suppliers, supplier_id, new_contact, new_email, new_address, new_balance):
    for s in suppliers:
        if s["supplier_id"] == supplier_id:
            s["contact"] = new_contact
            s["email"] = new_email
            s["address"] = new_address
            try:
                s["outstanding_balance"] = float(new_balance)
            except ValueError:
                print("Invalid balance value. Balance not updated.")
            print("Supplier updated successfully!")
            return
    print("Supplier not found.")


def record_new_arrivals():
    inventory = load_inventory()

    print("\n===== RECORD NEW STOCK ARRIVALS =====")
    item_id = input("Enter item ID: ")

    item_found = None
    for item in inventory:
        if item['item_id'] == item_id:
            item_found = item
            break

    if item_found is None:
        print("Item ID not found!")
        return

    while True:
        quantity_input = input("Enter quantity to add: ")
        try:
            quantity = int(quantity_input)
            if quantity <= 0:
                print("Quantity must be positive!")
                continue
            break
        except ValueError:
            print("Invalid quantity!")

    item_found['stock'] += quantity
    save_inventory(inventory)
    print(f"Stock updated for {item_found['item_name']}. New stock: {item_found['stock']}")


# ====================== SUPPLIER MENU ======================
def supplier_menu():
    supplier_id = input("Enter Supplier ID: ").strip()

    while True:
        print("\n==============================")
        print(f"  SHOPTRACK: SUPPLIER MENU ({supplier_id})")
        print("==============================")
        print("1. View Pending Orders")
        print("2. Update Order Status (Delivery/Payment)")
        print("3. Exit to Main Menu")

        choice = input("\nPlease select an option (1-3): ").strip()

        if not choice:
            print("Error: Input cannot be empty. Please try again.")
            continue

        if choice == "1":
            view_pending_orders(supplier_id)
        elif choice == "2":
            update_delivery_and_payment(supplier_id)
        elif choice == "3":
            print("Exiting Supplier Menu...")
            return
        else:
            print("Invalid selection. Please enter a number between 1 and 3.")


def view_pending_orders(supplier_id):
    print("\n" + "=" * 60)
    print(f"VIEWING PENDING RECORDS FOR SUPPLIER: {supplier_id}")
    print("=" * 60)

    found_any = False

    # 检查订单文件 (6_orders.txt) 中的待处理订单
    try:
        with open(ORDERS_FILE, "r") as file:
            header = file.readline().strip()
            if header:
                print("\n--- PENDING ORDERS ---")
                print(f"{'OrderID':<10} {'Details':<20} {'Delivery':<10} {'Payment':<10}")
                print("-" * 50)

                order_found = False
                for line in file:
                    data = line.strip().split(',')
                    if len(data) < 5:
                        continue

                    if data[1] == supplier_id:
                        delivery_status = data[3]
                        payment_status = data[4]

                        if delivery_status.upper() == "PENDING" or payment_status.upper() == "UNPAID":
                            order_details = data[2] if len(data) > 2 else "No details"
                            if len(order_details) > 20:
                                order_details = order_details[:17] + "..."
                            print(f"{data[0]:<10} {order_details:<20} {delivery_status:<10} {payment_status:<10}")
                            order_found = True
                            found_any = True

                if not order_found:
                    print("No pending orders found in orders file.")
            else:
                print("Order file is empty.")
    except FileNotFoundError:
        print("Order file not found.")

    # 检查支付文件 (5_payments.txt) 中的未支付记录
    try:
        with open(PAYMENTS_FILE, "r") as file:
            header = file.readline().strip()
            if header:
                print("\n--- UNPAID PAYMENTS ---")
                print(f"{'PaymentID':<10} {'Date':<12} {'Amount':<10} {'Status':<8} {'Remarks'}")
                print("-" * 60)

                payment_found = False
                for line in file:
                    data = line.strip().split(',')
                    if len(data) < 7:
                        continue

                    # 检查是否是供应商支付记录，状态为Unpaid，且供应商ID匹配
                    if data[2].upper() == "SUPPLIER" and data[3] == supplier_id and data[5].upper() == "UNPAID":
                        payment_id = data[0]
                        date = data[1]
                        amount = data[4]
                        status = data[5]
                        remarks = data[6] if len(data) > 6 else ""

                        if len(remarks) > 30:
                            remarks = remarks[:27] + "..."

                        print(f"{payment_id:<10} {date:<12} {amount:<10} {status:<8} {remarks}")
                        payment_found = True
                        found_any = True

                if not payment_found:
                    print("No unpaid payments found in payments file.")
            else:
                print("Payment file is empty.")
    except FileNotFoundError:
        print("Payment file not found.")

    if not found_any:
        print(f"\nNo pending records found for supplier {supplier_id}.")


def update_delivery_and_payment(supplier_id):
    print("\n--- UPDATE ORDER STATUS ---")
    order_id_input = input("Enter Order ID to update: ").strip().upper()

    try:
        with open(ORDERS_FILE, "r") as file:
            lines = file.readlines()
            if not lines:
                print("No orders found.")
                return

        updated_lines = []
        order_found = False

        # 处理标题行
        header = lines[0]
        updated_lines.append(header)

        for line in lines[1:]:
            data = line.strip().split(',')
            # 确保有7个字段：order_id,supplier_id,item_id,quantity,order_date,delivery_status,payment_status
            if len(data) < 7:
                updated_lines.append(line)  # 保留无效行（但标记问题）
                continue

            if data[0] == order_id_input:
                if data[1] != supplier_id:
                    print("Access Denied: You do not have permission for this order.")
                    return

                order_found = True
                print(f"Current Status: Delivery={data[5]}, Payment={data[6]}")
                print("Choose Update: 1. Delivered | 2. Paid | 3. Both | 4. Cancel")
                choice = input("Enter selection: ")

                if choice == "1":
                    data[5] = "Delivered"
                elif choice == "2":
                    data[6] = "Paid"
                elif choice == "3":
                    data[5] = "Delivered"
                    data[6] = "Paid"
                elif choice == "4":
                    print("Update cancelled.")
                    return
                else:
                    print("Invalid choice.")
                    return

                # 重建行（确保7个字段）
                line = ','.join(data) + '\n'

            updated_lines.append(line)

        if order_found:
            with open(ORDERS_FILE, "w") as file:
                file.writelines(updated_lines)
            print("Order successfully updated.")
        else:
            print(f"Order ID {order_id_input} not found.")

    except FileNotFoundError:
        print("Critical Error: 'orders.txt' not found.")

# ====================== HELPER FUNCTIONS ======================
def generate_unique_id(prefix, filename):
    try:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            with open(filename, 'w') as f:
                f.write("")
            lines = []

        if lines:
            last_id = lines[-1].split(',')[0]
            try:
                last_num = int(last_id.replace(prefix, ""))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"
    except Exception as e:
        print("Error generating ID:", e)
        return None


def hash_password(raw_password):
    total = 0
    for ch in raw_password:
        total += ord(ch)
    return hex(total)[2:].zfill(16)


def get_current_date():
    while True:
        date = input("Enter current date (YYYY-MM-DD): ").strip()
        if len(date) == 10 and date[4] == '-' and date[7] == '-':
            try:
                year = int(date[:4])
                month = int(date[5:7])
                day = int(date[8:10])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return date
                else:
                    print("Invalid date. Please use YYYY-MM-DD format.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        else:
            print("Invalid date format. Please use YYYY-MM-DD.")


def validate_credentials(username, password):
    try:
        with open(EMPLOYEE_FILE, 'r') as f:
            next(f)
            for line in f:
                data = line.strip().split(',')
                if len(data) >= 4 and data[1] == username:
                    stored_hash = data[3]
                    if hash_password(password) == stored_hash:
                        return True, data[2]
        return False, None
    except FileNotFoundError:
        print("Employee file not found.")
        return False, None


# ====================== MAIN EXECUTION ======================
if __name__ == "__main__":
    files = [
        (INVENTORY_FILE, "item_id,item_name,price,stock"),
        (SUPPLIER_FILE, "supplier_id,supplier_name,contact,email,address,outstanding_balance"),
        (SALES_FILE, "sale_id,item_id,quantity,total_amount,date"),
        (REFUNDS_FILE, "refund_id,item_id,quantity,refund_amount,date"),
        (PAYMENTS_FILE, "payment_id,date,payer_type,payer_id,amount,status,remarks"),
        (ORDERS_FILE, "order_id,supplier_id,order_details,delivery_status,payment_status"),
        (EMPLOYEE_FILE, "employee_id,username,role,password_hash,contact_info,join_date,status"),
        (CUSTOMER_FILE, "customer_id,name,contact,email")
    ]

    for file_path, header in files:
        try:
            with open(file_path, 'r') as f:
                pass
        except FileNotFoundError:
            with open(file_path, 'w') as f:
                f.write(header + "\n")

    ShopTrack_main()
