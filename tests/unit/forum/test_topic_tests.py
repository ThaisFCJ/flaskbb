from types import SimpleNamespace

import pytest

from flaskbb.forum.models import Post, Topic


class TestUpdateForumLastPost:
    @pytest.mark.parametrize(
        "username, title",
        [
            ("thais", "Primeiro tópico"),
            ("usuario2", "Segundo tópico"),
            ("usuario3", "Terceiro tópico"),
        ],
    )
    def test_updates_forum_last_post(self, username, title):
        user = SimpleNamespace(username=username)
        post = SimpleNamespace(user=user)
        forum = SimpleNamespace()

        topic = SimpleNamespace(
            forum=forum,
            title=title,
        )

        created = "data_teste"

        Post._update_forum_last_post(
            post, topic, user, created
        )

        assert forum.last_post is post
        assert forum.last_post_user is post.user
        assert forum.last_post_title == title
        assert forum.last_post_username == username
        assert forum.last_post_created == created

    def test_updates_last_post_with_different_user(self):
        post = SimpleNamespace(user="autor")
        forum = SimpleNamespace()

        topic = SimpleNamespace(
            forum=forum,
            title="Meu tópico",
        )

        user = SimpleNamespace(username="thais")

        Post._update_forum_last_post(
            post, topic, user, "data"
        )

        assert forum.last_post_user == "autor"
        assert forum.last_post_username == "thais"


def test_create_topic_saves_first_post(forum, user, monkeypatch):
    post = Post(content="Conteúdo do primeiro post")
    topic = Topic(title="Tópico de teste")

    initial_topic_count = forum.topic_count
    calls = []

    original_save = post.save

    def fake_save(post_user, post_topic):
        calls.append((post_user, post_topic))
        return original_save(
            user=post_user,
            topic=post_topic,
        )

    monkeypatch.setattr(post, "save", fake_save)

    topic._create_topic(user, forum, post)

    assert calls == [(user, topic)]

    assert topic.forum == forum
    assert topic.user == user
    assert topic.username == user.username
    assert topic.first_post == post
    assert topic.last_post == post
    assert forum.topic_count == initial_topic_count + 1

def test_topic_save_without_user_or_forum():
    topic = Topic(title="Tópico sem dados")

    result = topic.save()

    assert result is None


def test_topic_save_updates_existing_topic(topic):
    original_title = topic.title

    topic.title = "Título atualizado"
    result = topic.save()

    assert result is topic
    assert topic.title == "Título atualizado"
    assert topic.title != original_title


@pytest.mark.parametrize(
    "title",
    [
        "Tópico de teste A",
        "Tópico de teste B",
    ],
)
def test_topic_creation_sets_title(title, forum, user):
    post = Post(content="Conteúdo de teste")
    topic = Topic(title=title)

    result = topic.save(user=user, forum=forum, post=post)

    assert result is topic
    assert topic.title == title
    assert topic.first_post == post
    assert topic.last_post == post