import os
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from decimal import Decimal
from datetime import datetime
from collections import defaultdict


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

        self.cars_path = os.path.join(root_directory_path, "cars.txt")
        self.cars_index_path = os.path.join(root_directory_path, "cars_index.txt")
        self.models_path = os.path.join(root_directory_path, "models.txt")
        self.models_index_path = os.path.join(root_directory_path, "models_index.txt")
        self.sales_path = os.path.join(root_directory_path, "sales.txt")
        self.sales_index_path = os.path.join(root_directory_path, "sales_index.txt")

        os.makedirs(root_directory_path, exist_ok=True)

        for file_path in [
            self.cars_path,
            self.cars_index_path,
            self.models_path,
            self.models_index_path,
            self.sales_path,
            self.sales_index_path,
        ]:
            open(file_path, "a").close()

    # Задание 1. Сохранение моделей
    def add_model(self, model: Model) -> Model:
        data_line = f"{model.id};{model.name};{model.brand}".ljust(500) + "\n"
        with open(self.models_path, "r") as f:
            line_number = len(f.readlines())
        with open(self.models_path, "a") as f:
            f.write(data_line)

        index = []
        if os.path.exists(self.models_index_path):
            with open(self.models_index_path, "r") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) == 2:
                        index.append((int(parts[0]), int(parts[1])))
        index.append((model.id, line_number))
        index.sort()

        with open(self.models_index_path, "w") as f:
            for idx_id, idx_line in index:
                f.write(f"{idx_id};{idx_line}\n")

        return model

    # Задание 1. Сохранение автомобилей
    def add_car(self, car: Car) -> Car:
        data_line = f"{car.vin};{car.model};{car.price};{car.date_start};{car.status.value}".ljust(500) + "\n"
        with open(self.cars_path, "r") as f:
            line_number = len(f.readlines())
        with open(self.cars_path, "a") as f:
            f.write(data_line)

        index = []
        if os.path.exists(self.cars_index_path):
            with open(self.cars_index_path, "r") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) == 2:
                        index.append((parts[0], int(parts[1])))
        index.append((car.vin, line_number))
        index.sort()

        with open(self.cars_index_path, "w") as f:
            for vin, line_num in index:
                f.write(f"{vin};{line_num}\n")

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        data_line = f"{sale.sales_number};{sale.car_vin};{sale.sales_date.isoformat()};{sale.cost}".ljust(500) + "\n"
        with open(self.sales_path, "r") as f:
            line_number = len(f.readlines())
        with open(self.sales_path, "a") as f:
            f.write(data_line)

        index = []
        if os.path.exists(self.sales_index_path):
            with open(self.sales_index_path, "r") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) == 2:
                        index.append((parts[0], int(parts[1])))
        index.append((sale.sales_number, line_number))
        index.sort()

        with open(self.sales_index_path, "w") as f:
            for number, line_num in index:
                f.write(f"{number};{line_num}\n")

        car_line_number = None
        with open(self.cars_index_path, "r") as f:
            for line in f:
                vin, line_num_str = line.strip().split(";")
                if vin == sale.car_vin:
                    car_line_number = int(line_num_str)
                    break
        if car_line_number is None:
            raise ValueError(f"Car with VIN {sale.car_vin} not found.")

        with open(self.cars_path, "r") as f:
            f.seek(car_line_number * 501)
            car_line = f.readline().strip()

        parts = car_line.split(";")
        updated_car = Car(
            vin=parts[0],
            model=int(parts[1]),
            price=Decimal(parts[2]),
            date_start=datetime.fromisoformat(parts[3]),
            status=CarStatus.sold
        )
        new_data_line = f"{updated_car.vin};{updated_car.model};{updated_car.price};{updated_car.date_start.isoformat()};{updated_car.status.value}".ljust(500) + "\n"
        with open(self.cars_path, "r+") as f:
            f.seek(car_line_number * 501)
            f.write(new_data_line)

        return updated_car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        result = []
        index = []

        with open(self.cars_index_path, "r") as f:
            for line in f:
                vin, line_num_str = line.strip().split(";")
                index.append((vin, int(line_num_str)))

        index.sort(key=lambda x: x[1])

        with open(self.cars_path, "r") as f:
            for vin, line_number in index:
                f.seek(line_number * 501)
                line = f.readline().strip()

                if not line:
                    continue

                parts = line.split(";")
                if len(parts) < 5:
                    continue

                car = Car(
                    vin=parts[0],
                    model=int(parts[1]),
                    price=Decimal(parts[2]),
                    date_start=datetime.fromisoformat(parts[3]),
                    status=CarStatus(parts[4]),
                )

                if car.status == status:
                    result.append(car)

        return result

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        car_line_number = None

        with open(self.cars_index_path, "r") as index_file:
            for line in index_file:
                index_vin, line_num_str = line.strip().split(";")
                if index_vin == vin:
                    car_line_number = int(line_num_str)
                    break

        if car_line_number is None:
            return None

        with open(self.cars_path, "r") as cars_file:
            cars_file.seek(car_line_number * 501)
            line = cars_file.readline().strip()
            car_parts = line.split(";")

            if len(car_parts) < 5:
                return None

        car_model_id = int(car_parts[1])
        car_price = Decimal(car_parts[2])
        car_date_start = datetime.fromisoformat(car_parts[3])
        car_status = CarStatus(car_parts[4])

        model_line_number = None
        with open(self.models_index_path, "r") as index_file:
            for line in index_file:
                idx_id, idx_line = line.strip().split(";")
                if int(idx_id) == car_model_id:
                    model_line_number = int(idx_line)
                    break

        if model_line_number is None:
            return None

        with open(self.models_path, "r") as models_file:
            models_file.seek(model_line_number * 501)
            model_line = models_file.readline().strip()
            model_parts = model_line.split(";")

            if len(model_parts) < 3:
                return None

        model_name = model_parts[1]
        model_brand = model_parts[2]

        sales_date = None
        sales_cost = None

        if car_status == CarStatus.sold:
            with open(self.sales_path, "r") as sales_file:
                for line in sales_file:
                    parts = line.strip().split(";")
                    if len(parts) < 4:
                        continue
                    if parts[1] == vin:
                        sales_date = datetime.fromisoformat(parts[2])
                        sales_cost = Decimal(parts[3])
                        break

        return CarFullInfo(
            vin=vin,
            car_model_name=model_name,
            car_model_brand=model_brand,
            price=car_price,
            date_start=car_date_start,
            status=car_status,
            sales_date=sales_date,
            sales_cost=sales_cost,
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        index = []
        car_line_number = None

        with open(self.cars_index_path, "r") as f:
            for line in f:
                vin_index, line_num_str = line.strip().split(";")
                line_num = int(line_num_str)
                index.append((vin_index, line_num))
                if vin_index == vin:
                    car_line_number = line_num

        if car_line_number is None:
            raise ValueError(f"Car with VIN {vin} not found")

        with open(self.cars_path, "r") as f:
            f.seek(car_line_number * 501)
            line = f.readline().strip()
            parts = line.split(";")
            if len(parts) < 5:
                raise ValueError("Corrupted car record")

        updated_car = Car(
            vin=new_vin,
            model=int(parts[1]),
            price=Decimal(parts[2]),
            date_start=datetime.fromisoformat(parts[3]),
            status=CarStatus(parts[4])
        )

        new_data_line = f"{updated_car.vin};{updated_car.model};{updated_car.price};{updated_car.date_start.isoformat()};{updated_car.status.value}".ljust(500) + "\n"
        with open(self.cars_path, "r+") as f:
            f.seek(car_line_number * 501)
            f.write(new_data_line)

        new_index = []
        for vin_index, line_num in index:
            if vin_index == vin:
                new_index.append((new_vin, line_num))
            else:
                new_index.append((vin_index, line_num))

        new_index.sort()  # по VIN

        with open(self.cars_index_path, "w") as f:
            for vin_index, line_num in new_index:
                f.write(f"{vin_index};{line_num}\n")

        return updated_car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        sale_line_number = None
        sale_vin = None

        with open(self.sales_index_path, "r") as f:
            for line in f:
                num, line_num = line.strip().split(";")
                if num == sales_number:
                    sale_line_number = int(line_num)
                    break

        if sale_line_number is None:
            raise ValueError(f"Sale with number {sales_number} not found.")

        with open(self.sales_path, "r") as f:
            f.seek(sale_line_number * 501)
            sale_line = f.readline().strip()
            parts = sale_line.split(";")
            if len(parts) < 4:
                raise ValueError("Corrupted sale record")
            sale_vin = parts[1]

        new_sales_lines = []
        new_sales_index = []

        with open(self.sales_path, "r") as f:
            for i, line in enumerate(f):
                if i == sale_line_number:
                    continue
                new_sales_lines.append(line)

        with open(self.sales_index_path, "r") as f:
            for line in f:
                num, line_num = line.strip().split(";")
                if num == sales_number:
                    continue
                new_sales_index.append((num, int(line_num)))

        with open(self.sales_path, "w") as f:
            for line in new_sales_lines:
                f.write(line)

        with open(self.sales_index_path, "w") as f:
            for i, (num, _) in enumerate(new_sales_index):
                f.write(f"{num};{i}\n")

        car_line_number = None
        with open(self.cars_index_path, "r") as f:
            for line in f:
                vin, line_num_str = line.strip().split(";")
                if vin == sale_vin:
                    car_line_number = int(line_num_str)
                    break

        if car_line_number is None:
            raise ValueError(f"Car with VIN {sale_vin} not found.")

        with open(self.cars_path, "r") as f:
            f.seek(car_line_number * 501)
            car_line = f.readline().strip()

        parts = car_line.split(";")
        if len(parts) < 5:
            raise ValueError("Corrupted car record")

        updated_car = Car(
            vin=parts[0],
            model=int(parts[1]),
            price=Decimal(parts[2]),
            date_start=datetime.fromisoformat(parts[3]),
            status=CarStatus.available
        )

        new_car_line = f"{updated_car.vin};{updated_car.model};{updated_car.price};{updated_car.date_start.isoformat()};{updated_car.status.value}".ljust(500) + "\n"

        with open(self.cars_path, "r+") as f:
            f.seek(car_line_number * 501)
            f.write(new_car_line)

        return updated_car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:

        model_sales_count: dict[int, int] = defaultdict(int)
        car_model_map = {}

        index = []
        with open(self.cars_index_path, "r") as f:
            for line in f:
                vin, line_num_str = line.strip().split(";")
                index.append((vin, int(line_num_str)))

        with open(self.cars_path, "r") as f:
            for vin, line_number in index:
                f.seek(line_number * 501)
                line = f.readline().strip()
                parts = line.split(";")
                if len(parts) >= 2:
                    car_model_map[vin] = int(parts[1])

        with open(self.sales_path, "r") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) < 4:
                    continue
                vin = parts[1]
                model_id = car_model_map.get(vin)
                if model_id is not None:
                    model_sales_count[model_id] += 1

        sorted_model_ids = sorted(model_sales_count.items(), key=lambda x: -x[1])[:3]
        top_model_ids = [model_id for model_id, _ in sorted_model_ids]

        model_line_map = {}
        with open(self.models_index_path, "r") as f:
            for line in f:
                model_id_str, line_num_str = line.strip().split(";")
                model_line_map[int(model_id_str)] = int(line_num_str)

        result = []
        with open(self.models_path, "r") as f:
            for model_id in top_model_ids:
                line_number = model_line_map.get(model_id)
                if line_number is None:
                    continue

                f.seek(line_number * 501)
                model_line = f.readline().strip()
                parts = model_line.split(";")
                if len(parts) < 3:
                    continue

                result.append(ModelSaleStats(
                    car_model_name=parts[1],
                    brand=parts[2],
                    sales_number=model_sales_count[model_id]
                ))

        return result
