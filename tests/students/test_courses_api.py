import pytest
from django.urls import reverse
from rest_framework import status
from model_bakery import baker
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient
from students.models import Course


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory():
    def create_course(**kwargs):
        return baker.make('Course', **kwargs)

    return create_course


@pytest.fixture
def student_factory():
    def create_student(**kwargs):
        return baker.make('Student', **kwargs)

    return create_student


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    # Создаем курс через фабрику
    course = course_factory()

    # Строим URL для получения курса
    url = reverse('courses-detail', kwargs={'pk': course.id})

    # Делаем запрос через тестовый клиент
    response = api_client.get(url)

    # Проверяем код возврата и данные курса
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == course.id


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    # Создаем несколько курсов через фабрику
    course_factory(_quantity=3)

    # Строим URL для списка курсов
    url = reverse('courses-list')

    # Делаем запрос через тестовый клиент
    response = api_client.get(url)

    # Проверяем код возврата и количество курсов в ответе
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    # Создаем несколько курсов через фабрику
    courses = course_factory(_quantity=3)
    course_id = courses[0].id

    # Строим URL для списка курсов с фильтрацией по id
    url = reverse('courses-list') + f'?id={course_id}'

    # Делаем запрос через тестовый клиент
    response = api_client.get(url)

    # Проверяем код возврата и что вернулся только один курс
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == course_id


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    # Создаем курс с определенным именем
    course = course_factory(name="Test Course")

    # Строим URL для списка курсов с фильтрацией по имени
    url = reverse('courses-list') + '?name=Test Course'

    # Делаем запрос через тестовый клиент
    response = api_client.get(url)

    # Проверяем код возврата и что вернулся курс с нужным именем
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Test Course"


@pytest.mark.django_db
def test_create_course(api_client):
    # Подготавливаем JSON-данные
    course_data = {
        "name": "New Course",
        "description": "Course Description"
    }

    # Строим URL для создания курса
    url = reverse('courses-list')

    # Делаем POST запрос через тестовый клиент
    response = api_client.post(url, course_data, format='json')

    # Проверяем код возврата и данные созданного курса
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == "New Course"


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    # Создаем курс через фабрику
    course = course_factory()

    # Подготавливаем данные для обновления
    updated_data = {
        "name": "Updated Course",
        "description": "Updated Description"
    }

    # Строим URL для обновления курса
    url = reverse('courses-detail', kwargs={'pk': course.id})

    # Делаем PUT запрос через тестовый клиент
    response = api_client.put(url, updated_data, format='json')

    # Проверяем код возврата и обновленные данные курса
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == "Updated Course"


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    # Создаем курс через фабрику
    course = course_factory()

    # Строим URL для удаления курса
    url = reverse('courses-detail', kwargs={'pk': course.id})

    # Делаем DELETE запрос через тестовый клиент
    response = api_client.delete(url)

    # Проверяем код возврата и что курс был удален
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Course.objects.filter(id=course.id).count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("student_count, is_valid", [
    (19, True),
    (20, True),
    (21, False),
    (25, False),
])
def test_max_students_on_course(settings, course_factory, student_factory, student_count, is_valid):
    # Переопределяем настройку MAX_STUDENTS_PER_COURSE в тесте
    settings.MAX_STUDENTS_PER_COURSE = 20

    # Создаем курс через фабрику
    course = course_factory()

    # Создаем студентов
    students = student_factory(_quantity=21)

    # Добавляем студентов на курс
    course.students.set(students)

    # Проверяем валидацию
    if is_valid:
        try:
            course.clean()  # Вызываем валидацию вручную
        except ValidationError:
            pytest.fail("проблема с проверкой")
    else:
        with pytest.raises(ValidationError):
            course.clean()