# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta

from shows import tvstalker
from shows import models


tv = tvstalker.TvStalker()


def get_show(title, user):
    return tv.get_show(title, user)


def get_show_by_id(showid, user):
    return tv.get_show_by_id(showid, user)


def unfollow_show(showid, user):
    results = models.UserFollowing.objects.filter(user=user,
        showid=int(showid))
    if len(results) > 0:
        results[0].delete()


def follow_show(showid, user):
    show = models.Show.objects.filter(showid=int(showid))
    follow, created = models.UserFollowing.objects.get_or_create(user=user,
        showid=int(showid), show=show[0])
    if created:
        follow.save()


def user_is_following(showid, user):
    results = models.UserFollowing.objects.filter(user=user,
        showid=int(showid))
    if len(results) > 0:
        return True
    return False


def get_show_info(showid):
    show = models.Show.objects.filter(showid=int(showid))
    data = {}
    data['showid'] = show[0].showid
    data['title'] = show[0].title
    data['overview'] = show[0].overview
    data['poster'] = show[0].poster
    tv.get_episode_info_by_date(show[0], data)
    return data


def get_episodes_for_season(showid, season, episode):
    episode = models.Episode.objects.filter(showid=int(showid),
        season_nro=int(season), nro=int(episode))
    data = {}
    data['title'] = episode[0].name
    data['overview'] = episode[0].overview
    data['season'] = episode[0].season_nro
    data['nro'] = episode[0].nro
    data['airdate'] = episode[0].airdate
    return data


def get_seasons(showid):
    seasons = models.Season.objects.filter(showid=int(showid)).order_by('-nro')
    data = []
    for season in seasons:
        episodesdb = models.Episode.objects.filter(showid=int(showid),
            season_nro=season.nro).order_by('nro')
        episodes = []
        for episode in episodesdb:
            info = {}
            info['season'] = season.nro
            info['nro'] = episode.nro
            info['name'] = episode.name
            info['airdate'] = episode.airdate
            episodes.append(info)
        data.append((season.nro, episodes))
    return data


def get_shows_per_user(user, shows_filter):
    results = models.UserFollowing.objects.filter(user=user)

    shows = []
    today = datetime.date.today()
    yesterday = today - timedelta(days=1)
    for follow in results:
        if shows_filter == 'current' and not follow.show.current:
            continue

        data = {}
        data['showid'] = follow.show.showid
        data['title'] = follow.show.title
        data['poster'] = follow.show.poster
        if shows_filter == 'today':
            if not tv.get_episode_info_by_date(follow.show, data, today):
                continue
        elif shows_filter == 'yesterday':
            if not tv.get_episode_info_by_date(follow.show, data, yesterday):
                continue
        elif shows_filter in ('monday', 'tuesday', 'wednesday', 'thursday',
                              'friday', 'saturday', 'sunday'):
            if follow.show.dayofweek == shows_filter.title():
                tv.get_episode_info_by_date(follow.show, data)
            else:
                continue
        else:
            tv.get_episode_info_by_date(follow.show, data)
        shows.append(data)
    return {'shows': shows}


def get_most_rated_shows(user):
    results = models.Show.objects.all().order_by('-rated')
    following = models.UserFollowing.objects.filter(
        user=user).values_list('showid', flat=True)
    recommended = []
    for show in results:
        if len(recommended) == 2:
            break
        if show.showid not in following:
            data = {}
            data['showid'] = show.showid
            data['title'] = show.title
            data['overview'] = show.overview
            data['poster'] = show.poster
            tv.get_episode_info_by_date(show, data)
            recommended.append(data)
    return recommended