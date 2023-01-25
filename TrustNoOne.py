# 乱数のライブラリを読み込む
from random import randint
# pyxelを読み込む
import pyxel
import time
import threading
import subprocess
from enum import Enum, auto
# sns共有用ライブラリ
import webbrowser

#最初の文字
start_charactor="Start"
#風船の数変
balloon_quantity=5
#床の速さを変える
floor_speed=5
#ポーズする
pose_add=1

#背景の色を変える
st=12


class GAMEMODE(Enum):
    start = auto()
    main = auto()
    #pause = auto()
    result = auto()

class App:
    """
    Appクラス
    """
    def __init__(self):
        """
        クラスからインスタンスを生成する時に最初の呼ばれる関数
        """

        # Gameを初期化、画面作成
        self.fps = 35
        pyxel.init(160, 120, fps=self.fps) #経過時間カウントのためにFPS設定

        # 素材画像を読み込む
        pyxel.load("assets/material.pyxres")

        self.score = 0 #スコア
        self.lives = 3 #残機
        self.time = 0 #経過時間
        self.flame_count=0 #フレームカウント
        self.player_x = 72 #playerのx座標
        self.player_y = -16 #playerのy座標
        self.player_vy = 0 # playerのY方向の速度。vはvelocity（速度）
        self.player_is_alive = True # playerの生死を管理するフラグ。TrueまたはFalseが入る。
        self.result_score=0 #最終スコア
        self.result_time=0 #最終タイム

        # 背景の遠い雲の座標
        # self.far_cloud = [(-1, 7), (4, 6), (9, 6)]
        self.far_cloud = [(-10, 75), (40, 65), (90, 60)]
        # 背景の近い雲の座標
        # self.near_cloud = [(1, 2), (7, 3), (1, 1)]
        self.near_cloud = [(10, 25), (70, 35), (120, 15)]

        # 床の配置
        self.floor = [(i * 60, randint(8, 104), True) for i in range(4)]

        # フルーツの配置
        self.fruit = [(i * 60, randint(0, 104), randint(0, 2), True) for i in range(int(balloon_quantity))]
        self.i=0
        self.p=0

        # BGMの再生
        pyxel.play(0,0, loop=True)
        #ポーズするためのフラグ
        self.pose=0
        # スタート画面を選択
        self.gamemode = GAMEMODE.start
        # 実行
        pyxel.run(self.update,self.draw)

    def update(self):

        #選択した画面の表示に遷移
        if self.gamemode == GAMEMODE.start:
            self.update_start()
            # スコア0。他の変数も初期化
            self.score = 0
            self.time = 0
            self.lives = 3
            self.player_x = 72
            self.player_y = -16
            self.player_vy = 0
            self.player_is_alive = True

        elif self.gamemode == GAMEMODE.main:
            self.update_main()

        elif self.gamemode == GAMEMODE.result:
            self.update_result()

        # Qを押したら終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.pose==0:
        #経過時間更新
            self.update_time()
        # プレイヤーの更新
            self.update_player()
        # 床の更新
            for i, v in enumerate(self.floor):
                self.floor[i] = self.update_floor(*v)
        # フルーツの更新
            for i, v in enumerate(self.fruit):
                self.fruit[i] = self.update_fruit(*v)

    def update_start(self):
        pyxel.mouse(True)

        #スペースを押してメイン画面に遷移
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.gamemode = GAMEMODE.main
            self.pose = 0

        # スタートボタンを押してメイン画面に遷移
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (61 <= pyxel.mouse_x <= 87) and (96 <= pyxel.mouse_y <= 108):
            self.gamemode = GAMEMODE.main
            self.pose = 0


    def update_main(self):
        pyxel.mouse(False)
        if self.lives == 0:
            self.pose = 1
            self.gamemode = GAMEMODE.result

    def update_result(self):
        pyxel.mouse(True)

        # スペースを押してメイン画面に遷移
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.pose = 1
            self.gamemode = GAMEMODE.start

        # Retryボタンを押してメイン画面に遷移
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (104 <= pyxel.mouse_x <= 119) and (104 <= pyxel.mouse_y <= 119):
            self.pose = 1
            self.gamemode = GAMEMODE.start

        # Quitボタンを押して終了
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (128 <= pyxel.mouse_x <= 143) and (104 <= pyxel.mouse_y <= 119):
            pyxel.quit()

    def update_time(self):
        #経過時間カウント
        self.time += 1/self.fps
        self.flame_count+=1

    def update_player(self):
        # 左を押したら
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or  pyxel.btn(pyxel.GAMEPAD1_AXIS_LEFTX):
            # max(A, B)、AとBの大きい方を採用。このとき負にならないから画面外左側にはいかない
            self.player_x = max(self.player_x - 2, 0)

        # 右を押したら
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_AXIS_RIGHTX):
            # min(A, B)、AとBの小さい方を採用。画面外右側にはいかない
            self.player_x = min(self.player_x + 2, pyxel.width - 16)

        # 操作pad
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if 23 < pyxel.mouse_x < 57 and 88 < pyxel.mouse_y < 112:
                self.player_x = max(self.player_x - 2, 0)
            elif 103 < pyxel.mouse_x < 137 and 88 < pyxel.mouse_y < 112:
                self.player_x = min(self.player_x + 2, pyxel.width - 16)


        # 速度の分だけy方向プレイヤーを動かす
        self.player_y += self.player_vy
        # Y方向の最大値は8
        self.player_vy = min(self.player_vy + 1, 8)

        # プレイヤーのy座標が画面外にいったら
        if self.player_y > pyxel.height:
            if self.lives == 1: #残機が0になるとき死ぬ
                self.lives = 0
                self.result_score = self.score
                self.result_time = self.time

                if self.player_is_alive:
                    # 死んだ状態に
                    self.player_is_alive = False
                    pyxel.play(3, 5)

            else: # 0じゃなかったら残機数-1
                self.lives =self.lives-1
                self.player_x = 72
                self.player_y = -16
                self.player_vy = 0

    def update_floor(self, x, y, is_active):
        """
        床の更新
        """
        if is_active:
            if (
                self.player_x + 16 >= x
                and self.player_x <= x + 40
                and self.player_y + 16 >= y
                and self.player_y <= y + 8
                and self.player_vy > 0
            ):
                is_active = False
                self.score += 10
                self.player_vy = -12
                pyxel.play(3, 3)
        else:
            y += 6

        # 床を左に動かす
        x -= int(floor_speed)

        # 画面外に出たら
        if x < -40:
            # 画面右に移動
            x += 240
            y = randint(8, 104)
            is_active = True

        return x, y, is_active

    def update_fruit(self, x, y, kind, is_active):
        """
        フルーツの更新
        """

        # フルーツとプレイヤーの当たり判定
        # absは絶対値。x,y座標ともにプレイヤーとフルーツの距離が12より小さくなったら
        if is_active and abs(x - self.player_x) < 12 and abs(y - self.player_y) < 12:
            is_active = False
            # スコアを加算
            self.score += (kind + 1) * 100
            # 最小-8のスピードで上に飛ぶ
            self.player_vy = min(self.player_vy, -8)
            pyxel.play(3, 4)

        # 左に動かす
        x -= 2

        # 画面外左に出たら
        if x < -40:
            # 画面外、右に移動
            x += 240
            y = randint(0, 104)
            kind = randint(0, 2)
            is_active = True

        return (x, y, kind, is_active)

    def draw(self):
        #選択した画面の背景に遷移
        if self.gamemode == GAMEMODE.start:
            self.draw_start()
        elif self.gamemode == GAMEMODE.main:
            self.draw_main()
        elif self.gamemode == GAMEMODE.result:
            self.draw_result()

    def draw_start(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, 1, 0, 0, 160, 120, 0)
        pyxel.text(65, 100, start_charactor, 10)

        # 自分のツイッターアカウント
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (120 <= pyxel.mouse_x <= 135) and (88 <= pyxel.mouse_y <= 103):
            webbrowser.open("https://twitter.com/ChiikawaFanboy")


    def draw_result(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, 1, 0, 120, 160, 120, 5)

        # draw score
        s = "SCORE {:>4}".format(self.result_score)
        pyxel.text(25, 35, s, 1)
        pyxel.text(24, 35, s, 7)

        # draw time
        s = "TIME {:.3f}".format(self.result_time)
        pyxel.text(25, 64, s, 1)
        pyxel.text(24, 64, s, 7)

        # draw share
        pyxel.text(14, 94, "share score:", 10)

        # Score共有
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (64 <= pyxel.mouse_x <= 79) and (88 <= pyxel.mouse_y <= 103):
            template_link = "https://twitter.com/intent/tweet?text=TrustNoOne%0A%E3%80%90Score%E3%80%91{}%0A%E3%80%90Time%E3%80%91{:.1f}%0A%0A%E3%82%B2%E3%83%BC%E3%83%A0%E3%82%92%E9%81%8A%E3%81%B6%E2%86%93%0Ahttps%3A%2F%2Fsugi-ha.github.io%2FTrustNoOne%2F%0A%0Aby%20%40ChiikawaFanboy"
            form_link = template_link.format(self.result_score,self.result_time)
            webbrowser.open(form_link)

    def draw_main(self):
        """
        描画
        """
        # clear screen 画面をクリア
        pyxel.cls(5)

        # draw sky
        pyxel.blt(0, 88, 0, 0, 88, 160, 32, 12)

        # draw mountain
        pyxel.blt(0, 88, 0, 0, 64, 160, 24, 12)

        # draw forest
        offset = self.flame_count % 160
        for i in range(2):
             pyxel.blt(i * 160 - offset, 104, 0, 0, 48, 160, 16, 12)

        # draw cloud
        offset = (self.flame_count // 16) % 160
        for i in range(2):
            for x, y in self.far_cloud:
                pyxel.blt(x+i * 160 - offset, y, 0, 64, 32, 32, 8, 12)

        offset = (self.flame_count // 8) % 160
        for i in range(2):
            for x, y in self.near_cloud:
                pyxel.blt(x+i * 160 - offset, y, 0, 0, 32, 56, 8, 12)

        # draw floors
        for x, y, is_active in self.floor:
            pyxel.blt(x, y, 0, 0, 16, 40, 8, 12)

        # draw P
        for x, y, kind, is_active in self.fruit:
            if is_active:
                pyxel.blt(x, y, 0, 32 + kind * 16, 0, 16, 16, 12)

        # draw player
        pyxel.blt(
            self.player_x,
            self.player_y,
            0,
            16 if self.player_vy > 0 else 0,
            0,
            16,
            16,
            12,
        )

        # 操作Pad
        pyxel.rect(23,88,34,24,7)
        pyxel.rect(103,88,34,24,7)
        pyxel.tri(25, 100, 53, 92, 53, 108, 10)
        pyxel.tri(107, 92, 135, 100, 107, 108, 10)

        # draw time
        s = "TIME {:.3f}".format(self.time)
        pyxel.text(5, 4, s, 1)
        pyxel.text(4, 4, s, 7)

        # draw score
        s = "SCORE {:>4}".format(self.score)
        pyxel.text(85, 4, s, 1)
        pyxel.text(84, 4, s, 7)

        # draw lives
        s = "@-@{:>3}".format(self.lives)

        pyxel.text(135, 4, s, 1)
        pyxel.text(134, 4, s, 7)

App()
