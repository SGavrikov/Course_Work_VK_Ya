Одна из задач:   
"Сохранять указанное количество фотографий(по умолчанию 5) наибольшего размера (ширина/высота в пикселях) на Я.Диске"

Для фото, загруженных до 2012 года нет параметров ширины и высоты в результате запроса, при этом размер картинки (s-w) не однозначно определяет размер, поэтому в коде идет проверка размеров всех фото, сортировка по размеру. В связи с чем на больших объемах он медленный, но можно легко отсортировать альбом от "w" до "s", но точность будет ниже.
