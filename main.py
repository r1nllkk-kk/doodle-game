import random

WIDTH = 800
HEIGHT = 800

GRAVITY = 0.5
JUMP_SPEED = -13
MOVE_SPEED = 5

PLATFORM_IMAGES = ["ground_grass", "ground_sand", "ground_stone", "ground_wood", "ground_cake"]
PLATFORM_MARGIN_X = 100

COIN_TYPES = {
    "bronze": 10,
    "silver": 20,
    "gold": 30
}

MIN_GAP = 50
MAX_GAP = 90

JETPACK_SPAWN_CHANCE = 0.5
JETPACK_SPEED = -20
JETPACK_DURATION = 3.0

music.play("bg_music")
bunny = Actor("bunny")

platforms = []
traps = []
coins = []
jetpacks = []
game_over = False
score = 0
jetpack_active = False
jetpack_timer = 0.0

def generate_platforms(anchor_x=None):
    platforms.clear()
    traps.clear()
    coins.clear()
    jetpacks.clear()
    y = HEIGHT - 60
    x = anchor_x if anchor_x is not None else random.randint(PLATFORM_MARGIN_X, WIDTH - PLATFORM_MARGIN_X)

    while y > 0:
        platform = Actor(random.choice(PLATFORM_IMAGES))
        platform.pos = (x, y)
        platforms.append(platform)
        y -= random.randint(MIN_GAP, MAX_GAP)
        x = random.randint(PLATFORM_MARGIN_X, WIDTH - PLATFORM_MARGIN_X)

    if len(platforms) > 1:
        num_traps = random.randint(1, min(3, len(platforms) - 1))
        trap_platforms = random.sample(platforms[1:], num_traps)
        for platform in trap_platforms:
            trap = Actor("spikes")
            trap.x = platform.x
            trap.bottom = platform.top
            traps.append(trap)

    coin_candidates = [p for p in platforms[1:] if p not in trap_platforms]
    if coin_candidates:
        num_coins = random.randint(1, min(5, len(coin_candidates)))
        coin_platforms = random.sample(coin_candidates, num_coins)

        for platform in coin_platforms:
            coin_image, coin_value = random.choice(list(COIN_TYPES.items()))
            coin = Actor(coin_image)
            coin.value = coin_value
            coin.x = platform.x
            coin.bottom = platform.top
            coins.append(coin)

    jetpack_candidates = [p for p in platforms[1:] if p not in trap_platforms]
    if jetpack_candidates and random.random() < JETPACK_SPAWN_CHANCE:
        platform = random.choice(jetpack_candidates)
        jetpack = Actor("jetpack")
        jetpack.x = platform.x
        jetpack.bottom = platform.top
        jetpacks.append(jetpack)

generate_platforms()

vx = 0
vy = 0

def reset_bunny():
    global vx, vy, game_over, score, jetpack_active, jetpack_timer
    game_over = False
    score = 0
    jetpack_active = False
    jetpack_timer = 0.0
    generate_platforms()
    first_platform = platforms[0]
    bunny.x = first_platform.x
    bunny.bottom = first_platform.top - 60
    vx = 0
    vy = 0
    music.play("bg_music")

reset_bunny()

def update(dt=1/60):
    global vx, vy, game_over, score, jetpack_active, jetpack_timer

    if game_over:
        if keyboard.space:
            reset_bunny()
        return

    if keyboard.left:
        vx = -MOVE_SPEED
    elif keyboard.right:
        vx = MOVE_SPEED
    else:
        vx = 0

    prev_bottom = bunny.bottom

    if jetpack_active:
        jetpack_timer -= dt
        if jetpack_timer <= 0:
            jetpack_active = False
        vy = JETPACK_SPEED
    else:
        vy += GRAVITY

    bunny.y += vy
    bunny.x += vx

    if bunny.x < 0:
        bunny.x = WIDTH
    elif bunny.x > WIDTH:
        bunny.x = 0

    if not jetpack_active and vy > 0:
        for platform in platforms:
            if prev_bottom <= platform.top <= bunny.bottom and platform.left < bunny.x < platform.right:
                vy = JUMP_SPEED
                break

    for coin in coins[:]:
        if bunny.colliderect(coin):
            coins.remove(coin)
            score += coin.value
            sounds.coin_collect.play()

    for jetpack in jetpacks[:]:
        if bunny.colliderect(jetpack):
            jetpacks.remove(jetpack)
            jetpack_active = True
            jetpack_timer = JETPACK_DURATION
            sounds.jetpack_collect.play()

    if not jetpack_active:
        for trap in traps:
            if bunny.colliderect(trap):
                game_over = True
                sounds.hit_trap.play()
                music.stop()
                return

    if bunny.bottom < 0:
        generate_platforms(anchor_x=bunny.x)
        safety_platform = platforms[0]
        bunny.x = safety_platform.x
        bunny.bottom = safety_platform.top
        vy = JUMP_SPEED

    if bunny.top > HEIGHT:
        reset_bunny()

def draw():
    screen.fill((70, 130, 227))
    for platform in platforms:
        platform.draw()
    for trap in traps:
        trap.draw()
    for coin in coins:
        coin.draw()
    for jetpack in jetpacks:
        jetpack.draw()
    bunny.draw()

    screen.draw.text(f"Coins: {score}", (10, 10), fontsize=24, color="black")
    if jetpack_active:
        screen.draw.text(f"Jetpack: {max(0.0, jetpack_timer):.1f}с", (10, 40), fontsize=24, color="yellow")

    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=64, color="#4817bd")
        screen.draw.text("You triggered a trap.!", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=32, color="white")
        screen.draw.text("Press SPACE to start again", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=24, color="yellow")
