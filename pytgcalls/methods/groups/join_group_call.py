import asyncio
import os

from ...exceptions import InvalidStreamMode
from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...scaffold import Scaffold
from ...stream_type import StreamType


class JoinGroupCall(Scaffold):
    async def join_group_call(
        self,
        chat_id: int,
        file_audio_path: str,
        file_video_path: str = None,
        bitrate: int = 48000,
        invite_hash: str = None,
        join_as=None,
        stream_type: StreamType = None,
    ):
        if join_as is None:
            join_as = self._cache_local_peer
        if stream_type is None:
            stream_type = StreamType().local_stream
        if stream_type.stream_mode == 0:
            raise InvalidStreamMode()
        self._cache_user_peer.put(chat_id, join_as)
        bitrate = 48000 if bitrate > 48000 else bitrate
        if file_video_path is not None:
            if not os.path.isfile(file_video_path):
                raise FileNotFoundError()
        if not os.path.isfile(file_audio_path):
            raise FileNotFoundError()
        if self._app is not None:
            if self._wait_until_run is not None:
                if not self._wait_until_run.done():
                    await self._wait_until_run
                chat_call = await self._app.get_full_chat(
                    chat_id,
                )
                if chat_call is not None:
                    async def internal_sender():
                        request = {
                            'action': 'join_call',
                            'chat_id': chat_id,
                            'file_audio_path': file_audio_path,
                            'invite_hash': invite_hash,
                            'bitrate': bitrate,
                            'buffer_long': stream_type.stream_mode,
                        }
                        if file_video_path is not None:
                            request['file_video_path'] = file_video_path
                        await self._binding.send(request)
                    asyncio.ensure_future(internal_sender())
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()

