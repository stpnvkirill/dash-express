Данные - это сердце любого дашборда, поэтому к получению таблицы нужно отнестись с максимальным вниманием. Оптимизированный DataFrame  позволит ускорить вычисления и снизит потребление памяти.

Для оптимизации производительности можно использовать собственные методы Pandas. Ниже рассмотрено несколько базовых практик, которые позволят эффективно хранить и обрабатывать большие наборы данных.

<details markdown="1">
<summary>Совет 1: Не загружайте лишние данные</summary>

Загружайте только те колонки, которые будут использованы для построяния визуализаций и/или фильтрации

```python
pd.read_csv('data.csv', usecols=['only', 'used', 'columns'])
```
</details>

<details markdown="1">
<summary>Совет 2: Используйте подходящие типы данных</summary>

We can optimize the data types to reduce memory usage. By using the memory_usage() function, we can find the memory used by the data objects. It returns a series with an index of the original column names and values representing the amount of memory used by each column in bytes.

The syntax of memory_usgae() as follows:

```python
DataFrame.memory_usage(index=True, deep=False)
```

For numeric data, use the smallest possible data types  
In this code, columnsTMax of the int64 datatype is converted into the int32 datatype using the .astype() method. We can see the difference between the memory used by the TMax column. There is a decrease in memory usage.

```python
data = pd.read_csv('https://raw.githubusercontent.com/toddwschneider/nyc-taxi-data/master/data/central_park_weather.csv')
print("Initially Memory usage:")
print(data[['TMAX']].memory_usage(index=True, deep=False))
print()
data[['TMAX']]=data[['TMAX']].astype('int32')
print("Memory used after optimization:")
print(data[['TMAX']].memory_usage(index=True, deep=False))
```
```
Initially Memory usage:
Index      128
TMAX     39432
TMIN     39432
dtype: int64

Memory used after optimization:
Index     128
TMAX     4929
TMIN     4929
dtype: int64
```

For non-numeric columns of Data Frame are assigned as object data types which can be changed to category data types. Usually, the non-numerical feature column has categorical variables which are mostly repeating. 

```python
import pandas as pd
data = pd.read_csv('https://raw.githubusercontent.com/toddwschneider/nyc-taxi-data/master/data/central_park_weather.csv')

print("Initially Memory usage:")
print(data['NAME'].dtypes)
print(data['NAME'].memory_usage())
print()
data['NAME']=data['NAME'].astype('category')
print("Memory used after optimization:")
print(data['NAME'].dtypes)
print(data['NAME'].memory_usage())
```
```
Initially Memory usage:
object
39560

Memory used after optimization:
category
5173
```
</details>


Объект Page должен содержать функцию получения данных, ниже пример получения данных с приминением оптимизации:


```python
def get_df():
    # We load only used columns
    df =  pd.read_csv('titanic.csv', usecols=['survived', 'age', 'class', 'who', 'alone'])

    # Convert to the optimal data format
    df.age = df.age.fillna(0)
    df = df.astype(
        {
            'survived': 'int8',
            'age': 'int8',
            'class': 'category',
            'who': 'category',
            'alone': 'bool'
        }
    )  
    return df
```

Функцию получения данных необходимо передать во время инициализации объекта Page

```python
page = Page(
    ...
    getdf=get_df,               # Функция получения pd.DataFrame
    ...
    )
```
!!! note 
    Обратите внимание, что DashExpress кэширует DataFrame и не запрашивает данные при каждом запросе фильтрации.
