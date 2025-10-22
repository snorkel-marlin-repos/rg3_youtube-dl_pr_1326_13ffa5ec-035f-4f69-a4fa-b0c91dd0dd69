import socket

from .common import InfoExtractor

from ..utils import (
    compat_http_client,
    compat_urllib_error,
    compat_urllib_request,
    compat_str,
)


class SubtitlesIE(InfoExtractor):

    def _list_available_subtitles(self, video_id):
        """ outputs the available subtitles for the video """
        sub_lang_list = self._get_available_subtitles(video_id)
        sub_lang = ",".join(list(sub_lang_list.keys()))
        self.to_screen(u'%s: Available subtitles for video: %s' %
                       (video_id, sub_lang))

    def _extract_subtitles(self, video_id):
        """ returns {sub_lang: sub} or {} if subtitles not found """
        available_subs_list = self._get_available_subtitles(video_id)
        if not available_subs_list:  # error, it didn't get the available subtitles
            return {}
        if self._downloader.params.get('allsubtitles', False):
            sub_lang_list = available_subs_list
        else:
            if self._downloader.params.get('writesubtitles', False):
                if self._downloader.params.get('subtitleslangs', False):
                    requested_langs = self._downloader.params.get('subtitleslangs')
                elif 'en' in available_subs_list:
                    requested_langs = ['en']
                else:
                    requested_langs = [list(available_subs_list.keys())[0]]

                sub_lang_list = {}
                for sub_lang in requested_langs:
                    if not sub_lang in available_subs_list:
                        self._downloader.report_warning(u'no closed captions found in the specified language "%s"' % sub_lang)
                        continue
                    sub_lang_list[sub_lang] = available_subs_list[sub_lang]

        subtitles = {}
        for sub_lang, url in sub_lang_list.items():
            subtitle = self._request_subtitle_url(sub_lang, url)
            if subtitle:
                subtitles[sub_lang] = subtitle
        return subtitles

    def _request_subtitle_url(self, sub_lang, url):
        """ makes the http request for the subtitle """
        try:
            sub = compat_urllib_request.urlopen(url).read().decode('utf-8')
        except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
            self._downloader.report_warning(u'unable to download video subtitles for %s: %s' % (sub_lang, compat_str(err)))
            return
        if not sub:
            self._downloader.report_warning(u'Did not fetch video subtitles')
            return
        return sub

    def _get_available_subtitles(self, video_id):
        """ returns {sub_lang: url} or {} if not available """
        """ Must be redefined by the subclasses """
        pass

    def _request_automatic_caption(self, video_id, webpage):
        """ returns {sub_lang: sub} or {} if not available """
        """ Must be redefined by the subclasses """
        pass


class NoAutoSubtitlesIE(SubtitlesIE):
    """ A subtitle class for the servers that don't support auto-captions"""

    def _request_automatic_caption(self, video_id, webpage):
        self._downloader.report_warning(u'Automatic Captions not supported by this server')
        return {}
