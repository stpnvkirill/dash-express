Adding filters is very easy if you use DashExpress. You only need to specify the column by which filtering will take place and say the type of filtering multi = True|False

```python
page.add_autofilter('continent', multi=True)
```

You can also specify additional parameters of the Dash Mantine component.