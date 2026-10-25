// AI CITY — 3D Game World Simulation Engine (Three.js)
// Featuring stylized humanoid characters, detailed architecture, living traffic, and dynamic SQLite world state.

let scene, camera, renderer, controls;
let agents = [];
let buildings = {};
let vehicles = [];
let streetLamps = [];
let clouds = [];
let waterParticles = [];
let smokeParticles = [];
let sunLight, ambientLight;
let selectedAgent = null;
let worldTimeMinutes = 8 * 60; // Start at 08:00
let simulationSpeed = 1;
let raycaster, mouse;
let bubblesContainer;

// Standard colors & role mappings
const ROLE_CONFIGS = {
    "developer": { title: "Developer", color: 0x00f0ff, jacketColor: 0x0ea5e9, hairColor: 0x1e293b, icon: "👨‍💻", workPos: [-26, 0] },
    "reviewer": { title: "QA Reviewer", color: 0xf59e0b, jacketColor: 0xd97706, hairColor: 0x451a03, icon: "🔍", workPos: [-26, -20] },
    "manager": { title: "City Manager", color: 0xa855f7, jacketColor: 0x7c3aed, hairColor: 0x581c87, icon: "📋", workPos: [0, -22] },
    "researcher": { title: "Researcher", color: 0x10b981, jacketColor: 0x059669, hairColor: 0x064e3b, icon: "🔬", workPos: [26, -10] },
    "skill_mentor": { title: "Skill Mentor", color: 0x3b82f6, jacketColor: 0x2563eb, hairColor: 0x1e3a8a, icon: "🎓", workPos: [26, -10] },
    "architect": { title: "Arsitek Kota", color: 0xec4899, jacketColor: 0xdb2777, hairColor: 0x831843, icon: "📐", workPos: [26, 18] },
    "constructor": { title: "Mandor Konstruksi", color: 0xeab308, jacketColor: 0xca8a04, hairColor: 0x713f12, icon: "👷", workPos: [26, 18] },
    "data_analyst": { title: "Data Analyst", color: 0x06b6d4, jacketColor: 0x0891b2, hairColor: 0x164e63, icon: "📊", workPos: [-26, 0] },
    "security_agent": { title: "Petugas Keamanan", color: 0x64748b, jacketColor: 0x475569, hairColor: 0x0f172a, icon: "🛡️", workPos: [0, -22] },
    "designer": { title: "UI/UX Designer", color: 0xf43f5e, jacketColor: 0xe11d48, hairColor: 0x881337, icon: "🎨", workPos: [-26, 0] }
};

// INITIALIZATION
function init() {
    const container = document.getElementById('canvas-container');
    bubblesContainer = document.getElementById('bubbles-container');

    // 1. Scene & Atmosphere
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xbbe1fa);
    scene.fog = new THREE.FogExp2(0xbbe1fa, 0.008);

    // 2. Camera
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.set(42, 34, 46);

    // 3. Renderer with Soft Shadows
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "high-performance" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    container.appendChild(renderer.domElement);

    // 4. Orbit Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.04;
    controls.minDistance = 8;
    controls.maxDistance = 110;
    controls.target.set(0, 2, 0);

    // 5. Lighting
    ambientLight = new THREE.AmbientLight(0xffffff, 0.55);
    scene.add(ambientLight);

    sunLight = new THREE.DirectionalLight(0xfffaed, 1.3);
    sunLight.position.set(50, 70, 40);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    sunLight.shadow.camera.near = 10;
    sunLight.shadow.camera.far = 180;
    sunLight.shadow.camera.left = -50;
    sunLight.shadow.camera.right = 50;
    sunLight.shadow.camera.top = 50;
    sunLight.shadow.camera.bottom = -50;
    sunLight.shadow.bias = -0.0005;
    scene.add(sunLight);

    // 6. Build World Elements
    buildGroundAndRoads();
    buildStaticDistricts();
    buildEnvironmentProps();
    spawnClouds();
    spawnVehicles();

    // 7. Load Dynamic Data from SQLite
    loadInitialWorldState();

    // 8. Event Listeners
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();
    window.addEventListener('click', onPointerClick);
    window.addEventListener('resize', onWindowResize);

    // 9. Start Main Loop
    animate();
    setInterval(updateWorldData, 2500);
}

// -----------------------------------------------------------------------------
// 1. GROUND, ROADS, AND SIDEWALKS
// -----------------------------------------------------------------------------
function buildGroundAndRoads() {
    // Lush Grass Ground
    const groundGeo = new THREE.PlaneGeometry(160, 160);
    const groundMat = new THREE.MeshStandardMaterial({ color: 0x4d7c2c, roughness: 0.85, metalness: 0.05 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Central Cobblestone Plaza
    const plazaGeo = new THREE.CylinderGeometry(15, 15.2, 0.15, 32);
    const plazaMat = new THREE.MeshStandardMaterial({ color: 0xd4c7b8, roughness: 0.7 });
    const plaza = new THREE.Mesh(plazaGeo, plazaMat);
    plaza.position.set(0, 0.08, 0);
    plaza.receiveShadow = true;
    scene.add(plaza);

    // Plaza concentric decorative ring
    const ringGeo = new THREE.RingGeometry(13.5, 14.8, 32);
    const ringMat = new THREE.MeshStandardMaterial({ color: 0x8c7866, roughness: 0.6 });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(0, 0.17, 0);
    scene.add(ring);

    // Major Road Network with Sidewalks & Curbs
    createStreet(0, 0, 110, 8, false); // Main Horizontal Boulevard
    createStreet(0, 0, 8, 110, true);  // Main Vertical Avenue
    createStreet(-20, 0, 7, 90, true); // West Tech Avenue
    createStreet(20, 0, 7, 90, true);  // East Academy Avenue
    createStreet(0, 18, 90, 6, false); // Residential Street
    createStreet(0, -18, 90, 6, false);// Civic Street
}

function createStreet(x, z, w, h, isVertical) {
    // Asphalt Road Surface
    const roadMat = new THREE.MeshStandardMaterial({ color: 0x22262e, roughness: 0.85 });
    const road = new THREE.Mesh(new THREE.PlaneGeometry(w, h), roadMat);
    road.rotation.x = -Math.PI / 2;
    road.position.set(x, 0.1, z);
    road.receiveShadow = true;
    scene.add(road);

    // Concrete Sidewalks on both sides
    const curbMat = new THREE.MeshStandardMaterial({ color: 0xc8c3ba, roughness: 0.7 });
    const sidewalkWidth = 1.4;
    const sidewalkHeight = 0.16;

    if (isVertical) {
        // Left Sidewalk
        const swLeft = new THREE.Mesh(new THREE.BoxGeometry(sidewalkWidth, sidewalkHeight, h), curbMat);
        swLeft.position.set(x - w / 2 - sidewalkWidth / 2, sidewalkHeight / 2, z);
        swLeft.receiveShadow = true; scene.add(swLeft);
        // Right Sidewalk
        const swRight = new THREE.Mesh(new THREE.BoxGeometry(sidewalkWidth, sidewalkHeight, h), curbMat);
        swRight.position.set(x + w / 2 + sidewalkWidth / 2, sidewalkHeight / 2, z);
        swRight.receiveShadow = true; scene.add(swRight);
    } else {
        // Top Sidewalk
        const swTop = new THREE.Mesh(new THREE.BoxGeometry(w, sidewalkHeight, sidewalkWidth), curbMat);
        swTop.position.set(x, sidewalkHeight / 2, z - h / 2 - sidewalkWidth / 2);
        swTop.receiveShadow = true; scene.add(swTop);
        // Bottom Sidewalk
        const swBottom = new THREE.Mesh(new THREE.BoxGeometry(w, sidewalkHeight, sidewalkWidth), curbMat);
        swBottom.position.set(x, sidewalkHeight / 2, z + h / 2 + sidewalkWidth / 2);
        swBottom.receiveShadow = true; scene.add(swBottom);
    }

    // Yellow Double Center Lines
    const length = isVertical ? h : w;
    const stripeCount = Math.floor(length / 4.5);
    const lineMat = new THREE.MeshBasicMaterial({ color: 0xfacc15 });

    for (let i = -stripeCount / 2; i < stripeCount / 2; i++) {
        const stripeGeo = new THREE.PlaneGeometry(isVertical ? 0.22 : 2.0, isVertical ? 2.0 : 0.22);
        const stripe = new THREE.Mesh(stripeGeo, lineMat);
        stripe.rotation.x = -Math.PI / 2;
        if (isVertical) {
            stripe.position.set(x, 0.12, z + i * 4.5);
        } else {
            stripe.position.set(x + i * 4.5, 0.12, z);
        }
        scene.add(stripe);
    }
}

// -----------------------------------------------------------------------------
// 2. DETAILED ARCHITECTURAL BUILDINGS
// -----------------------------------------------------------------------------
function buildStaticDistricts() {
    // 1. TOWN HALL / CITY HALL (Classical Civic Architecture)
    const cityHall = new THREE.Group();
    // Stepped Base Platform
    const baseStep1 = new THREE.Mesh(new THREE.BoxGeometry(22, 0.8, 16), new THREE.MeshStandardMaterial({ color: 0xd1d5db }));
    baseStep1.position.y = 0.4;
    baseStep1.castShadow = true; baseStep1.receiveShadow = true;
    cityHall.add(baseStep1);
    const baseStep2 = new THREE.Mesh(new THREE.BoxGeometry(20, 0.8, 14), new THREE.MeshStandardMaterial({ color: 0xe5e7eb }));
    baseStep2.position.y = 1.2;
    baseStep2.castShadow = true; baseStep2.receiveShadow = true;
    cityHall.add(baseStep2);

    // Main Hall Body
    const hallBody = new THREE.Mesh(new THREE.BoxGeometry(18, 9, 12), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.4 }));
    hallBody.position.y = 5.7;
    hallBody.castShadow = true; hallBody.receiveShadow = true;
    cityHall.add(hallBody);

    // 6 Classical Fluted Columns
    for (let c = -7.5; c <= 7.5; c += 3) {
        const col = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.45, 8.5, 16), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 }));
        col.position.set(c, 5.5, 6.2);
        col.castShadow = true;
        cityHall.add(col);
    }

    // Triangular Pediment Roof
    const pediment = new THREE.Mesh(new THREE.ConeGeometry(11, 4, 4), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.3 }));
    pediment.rotation.y = Math.PI / 4;
    pediment.position.set(0, 11.8, 2.5);
    pediment.castShadow = true;
    cityHall.add(pediment);

    // Clock Tower & Spire
    const clockTower = new THREE.Mesh(new THREE.BoxGeometry(4, 7, 4), new THREE.MeshStandardMaterial({ color: 0xf1f5f9 }));
    clockTower.position.set(0, 13.5, -1.5);
    clockTower.castShadow = true;
    cityHall.add(clockTower);

    // Illuminated Clock Faces
    const clockFace = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.2, 16), new THREE.MeshBasicMaterial({ color: 0xfffbeb }));
    clockFace.rotation.x = Math.PI / 2;
    clockFace.position.set(0, 14.5, 0.6);
    cityHall.add(clockFace);

    // Golden Spire on top
    const spire = new THREE.Mesh(new THREE.ConeGeometry(1.6, 5, 8), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.8, roughness: 0.2 }));
    spire.position.set(0, 19.5, -1.5);
    cityHall.add(spire);

    // City Flags
    createFlag(cityHall, -7, 10.5, 5.5, 0x3b82f6);
    createFlag(cityHall, 7, 10.5, 5.5, 0xef4444);

    cityHall.position.set(0, 0, -26);
    scene.add(cityHall);
    buildings["city_hall"] = { name: "City Hall (Pemerintahan)", group: cityHall };

    // 2. TECH HUB / SOFTWARE OFFICE (Modern Cyber Skyscraper)
    const techTower = new THREE.Group();
    // Ground Atrium Lobby
    const lobby = new THREE.Mesh(new THREE.BoxGeometry(14, 5, 14), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2, metalness: 0.5 }));
    lobby.position.y = 2.5;
    lobby.castShadow = true; lobby.receiveShadow = true;
    techTower.add(lobby);

    // Canopy entrance
    const canopy = new THREE.Mesh(new THREE.BoxGeometry(6, 0.4, 4), new THREE.MeshStandardMaterial({ color: 0x00f0ff, roughness: 0.1 }));
    canopy.position.set(0, 3.2, 7.5);
    techTower.add(canopy);

    // Main Glass Tower (Middle Tier)
    const midTower = new THREE.Mesh(new THREE.BoxGeometry(11, 16, 11), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.1, metalness: 0.6 }));
    midTower.position.y = 13;
    midTower.castShadow = true;
    techTower.add(midTower);

    // Top Executive Tier
    const topTier = new THREE.Mesh(new THREE.BoxGeometry(8, 6, 8), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2, metalness: 0.7 }));
    topTier.position.y = 24;
    topTier.castShadow = true;
    techTower.add(topTier);

    // Glowing Neon Glass Window Bands
    for (let f = 5; f <= 23; f += 2.8) {
        const winBand = new THREE.Mesh(
            new THREE.BoxGeometry(11.2, 1.2, 11.2),
            new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x0088cc, emissiveIntensity: 0.6, roughness: 0.1 })
        );
        winBand.position.y = f;
        techTower.add(winBand);
    }

    // Helipad on roof
    const helipad = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 3.6, 0.2, 24), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6 }));
    helipad.position.set(0, 27.1, 0);
    techTower.add(helipad);
    const heliMarking = new THREE.Mesh(new THREE.RingGeometry(2.4, 2.8, 24), new THREE.MeshBasicMaterial({ color: 0xfacc15 }));
    heliMarking.rotation.x = -Math.PI / 2;
    heliMarking.position.set(0, 27.25, 0);
    techTower.add(heliMarking);

    // Blinking Radio Antenna Mast
    const antennaMast = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.25, 8), new THREE.MeshStandardMaterial({ color: 0x94a3b8 }));
    antennaMast.position.set(2.5, 31, 2.5);
    techTower.add(antennaMast);
    const beaconLight = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 8), new THREE.MeshBasicMaterial({ color: 0xff0044 }));
    beaconLight.position.set(2.5, 35, 2.5);
    techTower.add(beaconLight);

    // Glowing Billboard Sign "AI TECH CORP"
    const signBoard = new THREE.Mesh(new THREE.BoxGeometry(8, 1.6, 0.4), new THREE.MeshStandardMaterial({ color: 0x00f0ff, emissive: 0x00aacc, emissiveIntensity: 0.8 }));
    signBoard.position.set(0, 25.5, 4.2);
    techTower.add(signBoard);

    techTower.position.set(-28, 0, 0);
    scene.add(techTower);
    buildings["tech_hub"] = { name: "Software Tech Hub (Ari)", group: techTower };

    // 3. QA TESTING LAB (High-Tech Modular Lab)
    const qaLab = new THREE.Group();
    const labBody = new THREE.Mesh(new THREE.BoxGeometry(12, 7, 12), new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.4 }));
    labBody.position.y = 3.5;
    labBody.castShadow = true; qaLab.add(labBody);

    // Lab Entrance with warning stripes
    const entranceBay = new THREE.Mesh(new THREE.BoxGeometry(5, 4, 3), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
    entranceBay.position.set(0, 2, 6.5);
    qaLab.add(entranceBay);

    // Rotating Radar Dish on Roof
    const radarBase = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 1.0, 2), new THREE.MeshStandardMaterial({ color: 0x64748b }));
    radarBase.position.set(0, 8, 0);
    qaLab.add(radarBase);
    const radarDish = new THREE.Mesh(new THREE.SphereGeometry(2.5, 16, 16, 0, Math.PI), new THREE.MeshStandardMaterial({ color: 0xffffff, side: THREE.DoubleSide }));
    radarDish.rotation.x = -Math.PI / 3;
    radarDish.position.set(0, 9.5, 0);
    qaLab.add(radarDish);
    qaLab.userData.radar = radarDish;

    // Solar Panel Array on Roof
    for (let p = -4; p <= 4; p += 3) {
        const panel = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.2, 3), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, metalness: 0.7, roughness: 0.2 }));
        panel.rotation.x = Math.PI / 8;
        panel.position.set(p, 7.6, -3);
        qaLab.add(panel);
    }

    qaLab.position.set(-28, 0, -22);
    scene.add(qaLab);
    buildings["qa_lab"] = { name: "QA & Testing Lab (Bima)", group: qaLab };

    // 4. RESEARCH ACADEMY & MENTORSHIP ROTUNDA
    const academy = new THREE.Group();
    const rotundaPlatform = new THREE.Mesh(new THREE.CylinderGeometry(9, 9.5, 1.2, 32), new THREE.MeshStandardMaterial({ color: 0xe2e8f0 }));
    rotundaPlatform.position.y = 0.6;
    rotundaPlatform.castShadow = true; academy.add(rotundaPlatform);

    const rotundaBody = new THREE.Mesh(new THREE.CylinderGeometry(8, 8, 9, 32), new THREE.MeshStandardMaterial({ color: 0x2563eb, roughness: 0.3 }));
    rotundaBody.position.y = 5.7;
    rotundaBody.castShadow = true; academy.add(rotundaBody);

    // Arched Windows around rotunda
    for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
        const archWin = new THREE.Mesh(new THREE.BoxGeometry(1.6, 4.5, 0.4), new THREE.MeshBasicMaterial({ color: 0xfef08a }));
        archWin.position.set(Math.sin(a) * 8.05, 6, Math.cos(a) * 8.05);
        archWin.rotation.y = a;
        academy.add(archWin);
    }

    // Golden Geodesic Dome
    const dome = new THREE.Mesh(new THREE.SphereGeometry(7.8, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.7, roughness: 0.2 }));
    dome.position.y = 10.2;
    academy.add(dome);

    // Observatory Cupola
    const cupola = new THREE.Mesh(new THREE.SphereGeometry(2, 16, 16), new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.5 }));
    cupola.position.set(0, 17.5, 0);
    academy.add(cupola);

    academy.position.set(28, 0, -12);
    scene.add(academy);
    buildings["academy"] = { name: "Academy of Science (Deni & Eka)", group: academy };

    // 5. ACTIVE CONSTRUCTION ZONE & CRANE
    const conSite = new THREE.Group();
    // Concrete foundation slab
    const conSlab = new THREE.Mesh(new THREE.BoxGeometry(14, 0.6, 14), new THREE.MeshStandardMaterial({ color: 0x94a3b8 }));
    conSlab.position.y = 0.3;
    conSite.add(conSlab);

    // Steel Girder Framework (Building under construction)
    const steelMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.6 });
    for (let gx of [-5, 0, 5]) {
        for (let gz of [-5, 0, 5]) {
            const girder = new THREE.Mesh(new THREE.BoxGeometry(0.4, 8, 0.4), steelMat);
            girder.position.set(gx, 4, gz);
            conSite.add(girder);
        }
    }
    // Cross beams
    const beam1 = new THREE.Mesh(new THREE.BoxGeometry(10.4, 0.4, 0.4), steelMat);
    beam1.position.set(0, 8, 0); conSite.add(beam1);
    const beam2 = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 10.4), steelMat);
    beam2.position.set(0, 8, 0); conSite.add(beam2);

    // Animated Tower Crane
    const craneGroup = new THREE.Group();
    const craneMast = new THREE.Mesh(new THREE.BoxGeometry(0.8, 20, 0.8), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
    craneMast.position.set(6, 10, 6);
    craneGroup.add(craneMast);

    const boomArm = new THREE.Mesh(new THREE.BoxGeometry(18, 0.6, 0.6), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
    boomArm.position.set(0, 20.2, 6);
    craneGroup.add(boomArm);

    // Counterweight
    const counterWeight = new THREE.Mesh(new THREE.BoxGeometry(2, 1.5, 1.2), new THREE.MeshStandardMaterial({ color: 0x334155 }));
    counterWeight.position.set(7, 20.2, 6);
    craneGroup.add(counterWeight);

    // Crane Cable & Hook
    const hookCable = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 8), new THREE.MeshBasicMaterial({ color: 0x111111 }));
    hookCable.position.set(-4, 16, 6);
    craneGroup.add(hookCable);
    const hook = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.08, 8, 16, Math.PI), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
    hook.position.set(-4, 12, 6);
    hook.rotation.x = Math.PI;
    craneGroup.add(hook);

    conSite.add(craneGroup);
    conSite.userData.crane = craneGroup;

    // Safety Cones
    for (let sc = -6; sc <= 6; sc += 3) {
        createTrafficCone(conSite, sc, 0.3, 7.5);
    }

    conSite.position.set(28, 0, 18);
    scene.add(conSite);
    buildings["construction_site"] = { name: "Zona Ekspansi Kota", group: conSite };
}

function createFlag(parent, x, y, z, color) {
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 4), new THREE.MeshStandardMaterial({ color: 0xd1d5db }));
    pole.position.set(x, y + 2, z);
    parent.add(pole);
    const banner = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.0), new THREE.MeshStandardMaterial({ color: color, side: THREE.DoubleSide }));
    banner.position.set(x + 0.8, y + 3.2, z);
    parent.add(banner);
}

function createTrafficCone(parent, x, y, z) {
    const cone = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.8, 12), new THREE.MeshStandardMaterial({ color: 0xf97316 }));
    cone.position.set(x, y + 0.4, z);
    parent.add(cone);
}

// -----------------------------------------------------------------------------
// 3. DETAILED STYLIZED RESIDENTIAL COTTAGES
// -----------------------------------------------------------------------------
function createStylizedHouse(x, z, roofColorHex = 0xef4444) {
    const house = new THREE.Group();

    // 1. Foundation Base
    const stoneBase = new THREE.Mesh(new THREE.BoxGeometry(7.4, 0.6, 6.4), new THREE.MeshStandardMaterial({ color: 0x9ca3af, roughness: 0.8 }));
    stoneBase.position.y = 0.3;
    stoneBase.castShadow = true; stoneBase.receiveShadow = true;
    house.add(stoneBase);

    // 2. Timber House Walls
    const walls = new THREE.Mesh(new THREE.BoxGeometry(6.8, 4.4, 5.8), new THREE.MeshStandardMaterial({ color: 0xffedd5, roughness: 0.6 }));
    walls.position.y = 2.8;
    walls.castShadow = true; walls.receiveShadow = true;
    house.add(walls);

    // Corner wood trims
    const trimMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.7 });
    for (let cx of [-3.4, 3.4]) {
        for (let cz of [-2.9, 2.9]) {
            const trim = new THREE.Mesh(new THREE.BoxGeometry(0.3, 4.4, 0.3), trimMat);
            trim.position.set(cx, 2.8, cz);
            house.add(trim);
        }
    }

    // 3. Pitched Gabled Roof
    const roof = new THREE.Mesh(new THREE.ConeGeometry(5.4, 3.4, 4), new THREE.MeshStandardMaterial({ color: roofColorHex, roughness: 0.4 }));
    roof.rotation.y = Math.PI / 4;
    roof.position.y = 6.4;
    roof.castShadow = true;
    house.add(roof);

    // Dormer Roof Window
    const dormer = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.4, 1.4), new THREE.MeshStandardMaterial({ color: 0xffedd5 }));
    dormer.position.set(0, 6.0, 1.8);
    house.add(dormer);
    const dormerRoof = new THREE.Mesh(new THREE.ConeGeometry(1.4, 1.0, 4), new THREE.MeshStandardMaterial({ color: roofColorHex }));
    dormerRoof.rotation.y = Math.PI / 4;
    dormerRoof.position.set(0, 7.0, 1.8);
    house.add(dormerRoof);

    // 4. Front Porch & Wooden Steps
    const porchDeck = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.3, 2.0), trimMat);
    porchDeck.position.set(0, 0.45, 3.7);
    house.add(porchDeck);

    // Porch Posts
    for (let px of [-1.4, 1.4]) {
        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 2.4), trimMat);
        post.position.set(px, 1.6, 4.5);
        house.add(post);
    }

    // Front Door
    const door = new THREE.Mesh(new THREE.BoxGeometry(1.4, 2.6, 0.15), trimMat);
    door.position.set(0, 1.9, 2.92);
    house.add(door);

    // Glowing Windows with wooden frames
    const winMat = new THREE.MeshBasicMaterial({ color: 0xfef08a });
    const winL = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.4, 0.1), winMat);
    winL.position.set(-2.0, 2.8, 2.92); house.add(winL);
    const winR = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.4, 0.1), winMat);
    winR.position.set(2.0, 2.8, 2.92); house.add(winR);

    // 5. Brick Chimney
    const chimney = new THREE.Mesh(new THREE.BoxGeometry(1.0, 3.2, 1.0), new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.8 }));
    chimney.position.set(2.0, 6.8, -1.2);
    chimney.castShadow = true;
    house.add(chimney);

    // 6. Garden Picket Fence & Mailbox
    const fenceMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const fenceFront = new THREE.Mesh(new THREE.BoxGeometry(7.6, 0.6, 0.1), fenceMat);
    fenceFront.position.set(0, 0.3, 5.2);
    house.add(fenceFront);

    const mailbox = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.5, 0.6), new THREE.MeshStandardMaterial({ color: 0x2563eb }));
    mailbox.position.set(2.8, 1.0, 5.2);
    house.add(mailbox);

    house.position.set(x, 0, z);
    scene.add(house);
    return house;
}

// -----------------------------------------------------------------------------
// 4. ENVIRONMENT PROPS (Fountain, Foliage, Street Lamps)
// -----------------------------------------------------------------------------
function buildEnvironmentProps() {
    // 1. Animated Plaza Fountain
    const fountainGroup = new THREE.Group();
    // Basin 1
    const basin1 = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.6, 0.9, 24), new THREE.MeshStandardMaterial({ color: 0x94a3b8 }));
    basin1.position.y = 0.45; fountainGroup.add(basin1);
    // Basin 2
    const basin2 = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 2.8, 0.7, 24), new THREE.MeshStandardMaterial({ color: 0xcbd5e1 }));
    basin2.position.y = 1.6; fountainGroup.add(basin2);
    // Water pools
    const waterPool1 = new THREE.Mesh(new THREE.CylinderGeometry(3.9, 3.9, 0.2, 24), new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, transparent: true, opacity: 0.85 }));
    waterPool1.position.y = 0.8; fountainGroup.add(waterPool1);
    const waterPool2 = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 0.2, 24), new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, transparent: true, opacity: 0.85 }));
    waterPool2.position.y = 1.9; fountainGroup.add(waterPool2);
    // Central jet nozzle
    const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 1.2), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
    nozzle.position.y = 2.6; fountainGroup.add(nozzle);
    fountainGroup.position.set(0, 0, 0);
    scene.add(fountainGroup);

    // Spawn water spray particles
    for (let wp = 0; wp < 30; wp++) {
        const drop = new THREE.Mesh(new THREE.SphereGeometry(0.08, 6, 6), new THREE.MeshBasicMaterial({ color: 0xbae6fd }));
        drop.position.set((Math.random() - 0.5) * 1.5, 2.8 + Math.random() * 1.5, (Math.random() - 0.5) * 1.5);
        drop.userData = { vy: 0.05 + Math.random() * 0.05, initY: 2.8 };
        scene.add(drop);
        waterParticles.push(drop);
    }

    // 2. Stylized Foliage (Oak, Pine, Sakura)
    const treePositions = [
        [-8, -8, "oak"], [8, -8, "oak"], [-8, 8, "sakura"], [8, 8, "sakura"],
        [-16, -12, "pine"], [-16, 12, "pine"], [16, -22, "oak"], [16, 12, "pine"],
        [-34, -10, "sakura"], [-34, 14, "oak"], [34, -6, "pine"], [34, 16, "sakura"],
        [-12, -26, "oak"], [12, -26, "pine"], [-6, 26, "sakura"], [14, 26, "oak"]
    ];
    treePositions.forEach(([tx, tz, type]) => createStylizedTree(tx, tz, type));

    // 3. Street Lamps along Boulevards
    const lampPositions = [
        [-5, -4], [5, -4], [-5, 4], [5, 4],
        [-15, 0], [15, 0], [0, -14], [0, 14],
        [-24, -12], [-24, 12], [24, -12], [24, 12]
    ];
    lampPositions.forEach(([lx, lz]) => createOrnateStreetLamp(lx, lz));
}

function createStylizedTree(x, z, type = "oak") {
    const tree = new THREE.Group();
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5c2c16, roughness: 0.9 });
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.55, 2.5), trunkMat);
    trunk.position.y = 1.25; trunk.castShadow = true;
    tree.add(trunk);

    if (type === "oak") {
        // Multi-layered lush leafy spheres
        const oakMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.8 });
        const c1 = new THREE.Mesh(new THREE.SphereGeometry(2.2, 10, 10), oakMat);
        c1.position.y = 3.6; c1.castShadow = true; tree.add(c1);
        const c2 = new THREE.Mesh(new THREE.SphereGeometry(1.6, 8, 8), new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.8 }));
        c2.position.set(0.6, 4.4, 0.4); tree.add(c2);
    } else if (type === "pine") {
        // Conical Evergreen
        const pineMat = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.8 });
        for (let i = 0; i < 3; i++) {
            const cone = new THREE.Mesh(new THREE.ConeGeometry(2.4 - i * 0.5, 2.4, 8), pineMat);
            cone.position.y = 3.0 + i * 1.5; cone.castShadow = true;
            tree.add(cone);
        }
    } else {
        // Sakura Cherry Blossom
        const sakuraMat = new THREE.MeshStandardMaterial({ color: 0xf472b6, roughness: 0.8 });
        const s1 = new THREE.Mesh(new THREE.SphereGeometry(2.2, 10, 10), sakuraMat);
        s1.position.y = 3.6; s1.castShadow = true; tree.add(s1);
        const s2 = new THREE.Mesh(new THREE.SphereGeometry(1.5, 8, 8), new THREE.MeshStandardMaterial({ color: 0xfb7185 }));
        s2.position.set(-0.5, 4.2, -0.3); tree.add(s2);
    }

    tree.position.set(x, 0, z);
    scene.add(tree);
}

function createOrnateStreetLamp(x, z) {
    const lamp = new THREE.Group();
    const ironMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.8 });
    // Post
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.2, 4.5), ironMat);
    post.position.y = 2.25; lamp.add(post);
    // Curved arm
    const arm = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.1, 0.1), ironMat);
    arm.position.set(0.3, 4.4, 0); lamp.add(arm);
    // Lantern head
    const lantern = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.25, 0.6, 6), new THREE.MeshStandardMaterial({ color: 0xfffbeb, emissive: 0xfef08a, emissiveIntensity: 0.8 }));
    lantern.position.set(0.65, 4.1, 0); lamp.add(lantern);

    // Warm Point Light
    const light = new THREE.PointLight(0xfef08a, 0, 18);
    light.position.set(0.65, 4.0, 0);
    lamp.add(light);
    streetLamps.push(light);

    lamp.position.set(x, 0, z);
    scene.add(lamp);
}

// -----------------------------------------------------------------------------
// 5. LIVING CITY TRAFFIC (Moving 3D Cars)
// -----------------------------------------------------------------------------
function spawnVehicles() {
    const carTypes = [
        { color: 0xfacc15, name: "Taxi", speed: 0.08, z: -1.8, dir: 1 },
        { color: 0xef4444, name: "Sports", speed: 0.12, z: 1.8, dir: -1 },
        { color: 0x3b82f6, name: "Sedan", speed: 0.07, z: -1.8, dir: 1 },
        { color: 0xf8fafc, name: "Van", speed: 0.06, z: 1.8, dir: -1 }
    ];

    carTypes.forEach((cfg, idx) => {
        const car = new THREE.Group();
        const bodyMat = new THREE.MeshStandardMaterial({ color: cfg.color, metalness: 0.3, roughness: 0.4 });

        // Lower Chassis
        const chassis = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.8, 1.8), bodyMat);
        chassis.position.y = 0.6; chassis.castShadow = true; car.add(chassis);

        // Cabin / Roof
        const cabin = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.7, 1.6), new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2 }));
        cabin.position.set(-0.2, 1.35, 0); car.add(cabin);

        // 4 Spinning Wheels
        const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });
        const wheels = [];
        [[-1.1, -0.9], [1.1, -0.9], [-1.1, 0.9], [1.1, 0.9]].forEach(([wx, wz]) => {
            const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.3, 12), wheelMat);
            wheel.rotation.x = Math.PI / 2;
            wheel.position.set(wx, 0.35, wz);
            car.add(wheel);
            wheels.push(wheel);
        });

        // Headlights (Warm Yellow)
        const hlMat = new THREE.MeshBasicMaterial({ color: 0xfef08a });
        const hlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.2, 0.3), hlMat);
        hlLeft.position.set(1.8, 0.65, -0.6); car.add(hlLeft);
        const hlRight = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.2, 0.3), hlMat);
        hlRight.position.set(1.8, 0.65, 0.6); car.add(hlRight);

        // Taillights (Red)
        const tlMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
        const tlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.2, 0.3), tlMat);
        tlLeft.position.set(-1.8, 0.65, -0.6); car.add(tlLeft);
        const tlRight = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.2, 0.3), tlMat);
        tlRight.position.set(-1.8, 0.65, 0.6); car.add(tlRight);

        const initX = -40 + idx * 24;
        car.position.set(initX, 0, cfg.z);
        if (cfg.dir === -1) car.rotation.y = Math.PI;

        car.userData = {
            speed: cfg.speed,
            dir: cfg.dir,
            wheels: wheels,
            minX: -50,
            maxX: 50
        };

        scene.add(car);
        vehicles.push(car);
    });
}

// -----------------------------------------------------------------------------
// 6. ATMOSPHERIC DRIFTING CLOUDS
// -----------------------------------------------------------------------------
function spawnClouds() {
    const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, transparent: true, opacity: 0.85 });
    for (let c = 0; c < 8; c++) {
        const cloud = new THREE.Group();
        const puffCount = 4 + Math.floor(Math.random() * 4);
        for (let p = 0; p < puffCount; p++) {
            const puff = new THREE.Mesh(new THREE.SphereGeometry(2.5 + Math.random() * 2.0, 8, 8), cloudMat);
            puff.position.set(p * 2.2, (Math.random() - 0.5) * 1.2, (Math.random() - 0.5) * 2.0);
            cloud.add(puff);
        }
        cloud.position.set((Math.random() - 0.5) * 120, 36 + Math.random() * 12, (Math.random() - 0.5) * 120);
        cloud.userData = { speed: 0.02 + Math.random() * 0.03 };
        scene.add(cloud);
        clouds.push(cloud);
    }
}

// -----------------------------------------------------------------------------
// 7. HUMANOID CITIZEN CHARACTERS (NPCs WITH CLOTHES, HAIR, ARMS & PROPS)
// -----------------------------------------------------------------------------
function createHumanoidCharacter(agentData) {
    const group = new THREE.Group();
    const roleKey = agentData.role || "developer";
    const cfg = ROLE_CONFIGS[roleKey] || ROLE_CONFIGS["developer"];

    // 1. Torso & Jacket
    const torsoGeo = new THREE.BoxGeometry(0.8, 1.1, 0.5);
    const jacketMat = new THREE.MeshStandardMaterial({ color: cfg.jacketColor, roughness: 0.5 });
    const torso = new THREE.Mesh(torsoGeo, jacketMat);
    torso.position.y = 1.35;
    torso.castShadow = true;
    group.add(torso);

    // Collar / Inner Shirt
    const shirt = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.4, 0.1), new THREE.MeshStandardMaterial({ color: 0xffffff }));
    shirt.position.set(0, 1.68, 0.22);
    group.add(shirt);

    // 2. Head & Skin Tone
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xffdfba, roughness: 0.6 });
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.65, 0.6), skinMat);
    head.position.y = 2.25;
    head.castShadow = true;
    group.add(head);

    // Eyes / Glasses
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
    const eyeL = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 0.05), eyeMat);
    eyeL.position.set(-0.16, 2.28, 0.31); group.add(eyeL);
    const eyeR = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 0.05), eyeMat);
    eyeR.position.set(0.16, 2.28, 0.31); group.add(eyeR);

    // Hair / Hat Mesh
    const hairMat = new THREE.MeshStandardMaterial({ color: cfg.hairColor, roughness: 0.7 });
    if (roleKey === "constructor" || agentData.id.startsWith("agent_00")) {
        // Yellow Safety Hardhat
        const helmet = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.45, 0.28, 12), new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.3 }));
        helmet.position.y = 2.65; group.add(helmet);
        const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.08, 12), new THREE.MeshStandardMaterial({ color: 0xfacc15 }));
        brim.position.set(0, 2.54, 0.08); group.add(brim);
    } else {
        // Stylized Hair
        const hair = new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.35, 0.68), hairMat);
        hair.position.set(0, 2.62, -0.04); group.add(hair);
    }

    // 3. Articulated Legs & Shoes
    const pantsMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.7 });
    const shoeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 });

    const legLeftGroup = new THREE.Group();
    const legL = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.75, 0.3), pantsMat);
    legL.position.y = -0.37; legLeftGroup.add(legL);
    const shoeL = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.45), shoeMat);
    shoeL.position.set(0, -0.75, 0.06); legLeftGroup.add(shoeL);
    legLeftGroup.position.set(-0.25, 0.8, 0);
    group.add(legLeftGroup);

    const legRightGroup = new THREE.Group();
    const legR = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.75, 0.3), pantsMat);
    legR.position.y = -0.37; legRightGroup.add(legR);
    const shoeR = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.45), shoeMat);
    shoeR.position.set(0, -0.75, 0.06); legRightGroup.add(shoeR);
    legRightGroup.position.set(0.25, 0.8, 0);
    group.add(legRightGroup);

    // 4. Arms & Hands with Equipment Props
    const armMat = new THREE.MeshStandardMaterial({ color: cfg.jacketColor });
    const armL = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.75, 0.24), armMat);
    armL.position.set(-0.55, 1.35, 0); group.add(armL);
    const armR = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.75, 0.24), armMat);
    armR.position.set(0.55, 1.35, 0); group.add(armR);

    // Custom 3D Tool Held in Hand
    if (roleKey === "developer") {
        // Glowing Cyber Laptop
        const laptop = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.04, 0.4), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
        laptop.position.set(0, 1.1, 0.4); group.add(laptop);
        const screen = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.38, 0.04), new THREE.MeshBasicMaterial({ color: 0x00f0ff }));
        screen.position.set(0, 1.3, 0.58); screen.rotation.x = -0.2; group.add(screen);
    } else if (roleKey === "reviewer" || roleKey === "security_agent") {
        // Glowing Diagnostic Scanner
        const scanner = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.5, 0.06), new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xd97706, emissiveIntensity: 0.5 }));
        scanner.position.set(0.2, 1.15, 0.35); group.add(scanner);
    } else if (roleKey === "manager") {
        // Executive Tablet
        const tablet = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.55, 0.04), new THREE.MeshBasicMaterial({ color: 0xa855f7 }));
        tablet.position.set(0, 1.15, 0.35); group.add(tablet);
    } else {
        // Steel Construction Tool / Blueprint
        const tool = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.5), new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8 }));
        tool.rotation.x = Math.PI / 4;
        tool.position.set(0.3, 1.0, 0.3); group.add(tool);
    }

    group.userData = {
        id: agentData.id,
        name: agentData.name,
        role: agentData.role,
        info: {
            name: agentData.name,
            role: agentData.role,
            color: cfg.color,
            icon: cfg.icon,
            work: cfg.workPos || [0, 0],
            home: agentData.homePos || [0, 20]
        },
        legL: legLeftGroup,
        legR: legRightGroup,
        armL: armL,
        armR: armR,
        targetPos: new THREE.Vector3(cfg.workPos[0], 0, cfg.workPos[1]),
        walkSpeed: 0.04 + Math.random() * 0.02,
        walkCycle: Math.random() * Math.PI,
        thoughtText: `${agentData.name}: Berjalan menuju tempat kerja...`
    };

    return group;
}

// -----------------------------------------------------------------------------
// 8. BACKEND API BRIDGE — pywebview (desktop) ↔ HTTP (browser)
// -----------------------------------------------------------------------------
const API_BASE = "http://localhost:8000";
let _backendAvailable = null; // null = unknown, true/false after probe

async function _probeBackend() {
    if (_backendAvailable !== null) return _backendAvailable;
    try {
        const r = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(1200) });
        _backendAvailable = r.ok;
    } catch {
        _backendAvailable = false;
    }
    return _backendAvailable;
}

/** Unified API call: pywebview → HTTP → mock fallback */
async function apiCall(method, ...args) {
    // --- Desktop (pywebview) path ---
    if (window.pywebview && window.pywebview.api && window.pywebview.api[method]) {
        return await window.pywebview.api[method](...args);
    }
    // --- Browser HTTP path ---
    if (await _probeBackend()) {
        return await _httpCall(method, ...args);
    }
    // --- Pure offline mock ---
    return _mockCall(method, ...args);
}

async function _httpCall(method, ...args) {
    const endpoints = {
        get_llm_status:          () => fetch(`${API_BASE}/world/llm-status`).then(r => r.json()),
        get_initial_world_state: () => fetch(`${API_BASE}/world/state`).then(r => r.json()),
        get_world:               () => fetch(`${API_BASE}/world/status`).then(r => r.json()),
        get_events:              () => fetch(`${API_BASE}/world/events`).then(r => r.json()),
        submit_goal: async (goal) => {
            // 1. Create the task
            const task = await fetch(`${API_BASE}/tasks/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ goal, assigned_to: "agent_dev_01", priority: 5 })
            }).then(r => r.json());

            const taskId = task.id;

            // 2. Trigger immediate execution (don't wait for scheduler tick)
            await fetch(`${API_BASE}/tasks/${taskId}/run`, { method: "POST" }).catch(() => {});

            // 3. Poll for completion — PASSED or FAILED (up to 3 minutes)
            for (let i = 0; i < 180; i++) {
                await new Promise(r => setTimeout(r, 1000));
                const t = await fetch(`${API_BASE}/tasks/${taskId}`).then(r => r.json());
                if (t.status === "PASSED" || t.status === "FAILED") {
                    const res = t.result || {};
                    return {
                        status: t.status === "FAILED" ? "error" : "success",
                        goal: t.goal,
                        artifact_path: res.artifact_path || "solution.py",
                        review_status: res.review_status || "approved",
                        review_score: res.review_score || 0.95,
                        stdout: res.stdout || "",
                        stderr: res.stderr || "",
                        code: res.code || "",
                        new_building: res.new_building || null
                    };
                }
            }
            return { status: "error", goal, artifact_path: "", review_status: "timeout", review_score: 0, stdout: "⏱ Timeout — task masih berjalan, cek di /tasks", code: "" };
        },
        test_and_save_llm: (provider, apiKey, model, baseUrl) => fetch(`${API_BASE}/world/llm-config`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ provider, api_key: apiKey, model, base_url: baseUrl })
        }).then(r => r.json())
    };
    if (endpoints[method]) return await endpoints[method](...args);
    throw new Error(`No HTTP mapping for: ${method}`);
}

function _mockCall(method, ...args) {
    const mocks = {
        get_llm_status: () => ({ provider: "mock", model: "Offline Smart Engine", base_url: "" }),
        get_initial_world_state: () => ({
            population: 5,
            llm_provider: "mock",
            llm_model: "Offline Smart Engine",
            agents: [
                { id: "agent_dev_01",       name: "Ari",   role: "developer",   homePos: [-8, 22] },
                { id: "agent_reviewer_01",  name: "Bima",  role: "reviewer",    homePos: [0, 22]  },
                { id: "agent_manager_01",   name: "Citra", role: "manager",     homePos: [8, 22]  },
                { id: "agent_research_01",  name: "Deni",  role: "researcher",  homePos: [-8, 28] },
                { id: "agent_mentor_01",    name: "Eka",   role: "skill_mentor",homePos: [8, 28]  }
            ],
            buildings: []
        }),
        get_world: () => ({ population: agents.length }),
        get_events: () => [],
        submit_goal: (goal) => ({
            status: "success", goal,
            artifact_path: "solusi.py",
            review_status: "approved",
            review_score: 0.98,
            stdout: "✅ Simulasi offline: task diproses oleh Smart Engine.",
            code: `# Hasil kerja offline\nprint("Goal: ${goal.slice(0, 40)}")`
        }),
        test_and_save_llm: () => ({ success: true, message: "Konfigurasi tersimpan (offline mode)." })
    };
    return Promise.resolve(mocks[method] ? mocks[method](...args) : null);
}

// Show backend connection indicator on top bar
async function _showConnectionStatus() {
    const pill = document.getElementById('stat-llm');
    const hasDesktop = !!(window.pywebview && window.pywebview.api);
    const hasBackend = !hasDesktop && await _probeBackend();
    if (hasDesktop) {
        console.log("🖥️ AI City: Desktop mode (pywebview)");
    } else if (hasBackend) {
        console.log("🌐 AI City: Browser mode → FastAPI backend connected");
        // Add connection badge to top bar
        const badge = document.createElement('div');
        badge.className = 'stat-item';
        badge.innerHTML = '<span>🟢</span><span class="stat-value" style="color:#10b981;font-size:11px;">LIVE API</span>';
        document.getElementById('top-bar').insertBefore(badge, pill);
    } else {
        console.log("📴 AI City: Offline mode");
    }
}

// -----------------------------------------------------------------------------
// 9. DYNAMIC DATA LOADING (SYNCS SQLITE AGENTS & BUILDINGS)
// -----------------------------------------------------------------------------
async function loadInitialWorldState() {
    await _showConnectionStatus();
    try {
        const state = await apiCall("get_initial_world_state");
        if (state) {
            document.getElementById('stat-pop').innerText = `${state.population} Agents`;
            updateLlmStatusDisplay(state.llm_provider, state.llm_model);

            // 1. Render all Buildings from SQLite
            if (state.buildings && state.buildings.length > 0) {
                state.buildings.forEach((b, idx) => {
                    const colors = [0xef4444, 0x10b981, 0x8b5cf6, 0x06b6d4, 0xf59e0b];
                    createStylizedHouse(b.x, b.z, colors[idx % colors.length]);
                });
            } else {
                createStylizedHouse(-8, 22, 0xef4444);
                createStylizedHouse(0, 22, 0x10b981);
                createStylizedHouse(8, 22, 0x8b5cf6);
            }

            // 2. Spawn all Agents from SQLite
            if (state.agents && state.agents.length > 0) {
                state.agents.forEach((ag, idx) => {
                    if (!ag.homePos) {
                        ag.homePos = [-12 + (idx % 4) * 8, 22 + Math.floor(idx / 4) * 8];
                    }
                    spawnAgentToWorld(ag);
                });
            }
        }
    } catch (err) {
        console.error("Error loading world state:", err);
    }
}

function spawnAgentToWorld(agentData) {
    const agentMesh = createHumanoidCharacter(agentData);
    const home = agentMesh.userData.info.home;
    agentMesh.position.set(home[0], 0, home[1]);

    scene.add(agentMesh);
    agents.push(agentMesh);

    // Create 2D Overlay Bubble on Canvas
    const bubble = document.createElement('div');
    bubble.className = 'agent-bubble';
    bubble.id = `bubble-${agentData.id}`;
    bubble.innerHTML = `${agentMesh.userData.info.icon} ${agentData.name}: Berjalan...`;
    bubblesContainer.appendChild(bubble);
    agentMesh.userData.bubbleElem = bubble;

    if (agents.length === 1) {
        selectAgent(agentMesh);
    }
}

// -----------------------------------------------------------------------------
// 9. ANIMATION LOOP & SIMULATION
// -----------------------------------------------------------------------------
function animate() {
    requestAnimationFrame(animate);

    // 1. Advance Time & Day/Night Cycle
    worldTimeMinutes += (0.05 * simulationSpeed);
    if (worldTimeMinutes >= 24 * 60) worldTimeMinutes = 0;
    updateDayNightCycle(worldTimeMinutes);

    // 2. Animate Humanoid Characters
    agents.forEach(agent => {
        const u = agent.userData;
        const dx = u.targetPos.x - agent.position.x;
        const dz = u.targetPos.z - agent.position.z;
        const dist = Math.sqrt(dx * dx + dz * dz);

        if (dist > 0.6) {
            agent.position.x += (dx / dist) * u.walkSpeed * simulationSpeed;
            agent.position.z += (dz / dist) * u.walkSpeed * simulationSpeed;
            agent.lookAt(u.targetPos.x, agent.position.y, u.targetPos.z);

            // Walking limb swing & body bob
            u.walkCycle += 0.16 * simulationSpeed;
            u.legL.rotation.x = Math.sin(u.walkCycle) * 0.55;
            u.legR.rotation.x = -Math.sin(u.walkCycle) * 0.55;
            u.armL.rotation.x = -Math.sin(u.walkCycle) * 0.4;
            u.armR.rotation.x = Math.sin(u.walkCycle) * 0.4;
            agent.position.y = Math.abs(Math.sin(u.walkCycle * 2)) * 0.08;
        } else {
            // Rest or Switch destination
            agent.position.y = 0;
            u.legL.rotation.x = 0;
            u.legR.rotation.x = 0;

            if (u.targetPos.x === u.info.work[0]) {
                u.thoughtText = `${u.info.name}: Sedang bekerja di kantor...`;
                setTimeout(() => {
                    u.targetPos.set(u.info.home[0], 0, u.info.home[1]);
                }, 12000 / simulationSpeed);
            } else {
                u.thoughtText = `${u.info.name}: Beristirahat di rumah...`;
                setTimeout(() => {
                    u.targetPos.set(u.info.work[0], 0, u.info.work[1]);
                }, 8000 / simulationSpeed);
            }
        }

        // Project 2D Speech Bubble onto screen
        if (u.bubbleElem) {
            const headPos = agent.position.clone().add(new THREE.Vector3(0, 3.1, 0));
            headPos.project(camera);
            const x = (headPos.x * 0.5 + 0.5) * window.innerWidth;
            const y = (-(headPos.y * 0.5) + 0.5) * window.innerHeight;

            u.bubbleElem.style.left = `${x}px`;
            u.bubbleElem.style.top = `${y}px`;
            u.bubbleElem.innerHTML = `${u.info.icon} ${u.thoughtText}`;
            u.bubbleElem.style.opacity = (headPos.z < 1 && headPos.z > -1) ? '1' : '0';
        }
    });

    // 3. Animate Vehicles
    vehicles.forEach(car => {
        car.position.x += car.userData.speed * car.userData.dir * simulationSpeed;
        car.userData.wheels.forEach(w => w.rotation.z += 0.1 * car.userData.dir * simulationSpeed);

        if (car.userData.dir === 1 && car.position.x > car.userData.maxX) {
            car.position.x = car.userData.minX;
        } else if (car.userData.dir === -1 && car.position.x < car.userData.minX) {
            car.position.x = car.userData.maxX;
        }
    });

    // 4. Animate Drifting Clouds
    clouds.forEach(cl => {
        cl.position.x += cl.userData.speed * simulationSpeed;
        if (cl.position.x > 70) cl.position.x = -70;
    });

    // 5. Animate Fountain Water Spray
    waterParticles.forEach(p => {
        p.position.y += p.userData.vy * simulationSpeed;
        p.userData.vy -= 0.003 * simulationSpeed; // gravity
        if (p.position.y < p.userData.initY) {
            p.position.y = p.userData.initY;
            p.userData.vy = 0.05 + Math.random() * 0.04;
        }
    });

    // 6. Animate Radar Dish
    if (buildings["qa_lab"] && buildings["qa_lab"].group.userData.radar) {
        buildings["qa_lab"].group.userData.radar.rotation.y += 0.03 * simulationSpeed;
    }

    controls.update();
    renderer.render(scene, camera);
}

// DAY / NIGHT CYCLE
function updateDayNightCycle(mins) {
    const hours = mins / 60;
    const timeStr = `${String(Math.floor(hours)).padStart(2, '0')}:${String(Math.floor(mins % 60)).padStart(2, '0')}`;
    document.getElementById('stat-time').innerText = timeStr;

    const angle = (hours / 24) * Math.PI * 2 - Math.PI / 2;
    sunLight.position.x = Math.cos(angle) * 60;
    sunLight.position.y = Math.sin(angle) * 60;

    const isNight = hours < 5.5 || hours > 19;
    if (isNight) {
        scene.background.setHex(0x0a1128);
        scene.fog.color.setHex(0x0a1128);
        ambientLight.intensity = 0.18;
        sunLight.intensity = 0.15;
        streetLamps.forEach(l => l.intensity = 1.3);
    } else {
        scene.background.setHex(0xbbe1fa);
        scene.fog.color.setHex(0xbbe1fa);
        ambientLight.intensity = 0.6;
        sunLight.intensity = 1.3;
        streetLamps.forEach(l => l.intensity = 0);
    }
}

// -----------------------------------------------------------------------------
// 10. REAL DATA UPDATES & EVENT TICKER
// -----------------------------------------------------------------------------
async function updateWorldData() {
    try {
        const world = await apiCall("get_world");
        if (world && world.population) {
            document.getElementById('stat-pop').innerText = `${world.population} Agents`;
        }
        const events = await apiCall("get_events");
        if (events && events.length > 0) {
            const tickerList = document.getElementById('ticker-list');
            tickerList.innerHTML = '';
            events.slice(0, 5).forEach(e => {
                const item = document.createElement('div');
                item.className = 'ticker-item';
                item.innerText = formatEventMessage(e);
                tickerList.appendChild(item);
            });
        }
    } catch (e) {
        // Silent fallback — keep the last known state
    }
}

function formatEventMessage(evt) {
    const type = evt.type || "info";
    const p = evt.payload || {};
    if (type === "construction") {
        return `🏗️ Pembangunan: ${p.type === 'office' ? 'Gedung Kantor' : 'Rumah Hunian'} didirikan di (${p.position?.x}, ${p.position?.z})`;
    } else if (type === "recruitment") {
        return `👥 Warga Baru: ${p.name} (${p.role}) resmi bergabung dengan AI City!`;
    } else if (type === "task") {
        return `💼 Tugas: ${p.title || 'Pekerjaan baru'} sedang diproses...`;
    } else {
        return `📢 ${type.toUpperCase()}: ${p.action || JSON.stringify(p).slice(0, 40)}`;
    }
}

function addTickerItem(text) {
    const tickerList = document.getElementById('ticker-list');
    if (!tickerList) return;
    const item = document.createElement('div');
    item.className = 'ticker-item';
    item.innerText = text;
    tickerList.insertBefore(item, tickerList.firstChild);
    if (tickerList.children.length > 6) {
        tickerList.removeChild(tickerList.lastChild);
    }
}

// -----------------------------------------------------------------------------
// 11. USER INTERACTIONS & GOAL SUBMISSION
// -----------------------------------------------------------------------------
function setPresetGoal(text) {
    document.getElementById('task-input').value = text;
}

function openTaskModal() {
    document.getElementById('task-modal').style.display = 'block';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}

async function submitGoalFromGame() {
    const input = document.getElementById('task-input');
    const goal = input.value.trim();
    if (!goal) return;

    closeTaskModal();
    input.value = '';

    // Show banner
    const banner = document.getElementById('work-banner');
    const bannerTitle = document.getElementById('banner-title');
    const bannerDesc = document.getElementById('banner-desc');
    banner.style.display = 'block';
    bannerTitle.innerText = `⚙️ AGENT SEDANG MENGERJAKAN TUGAS...`;
    bannerDesc.innerText = `Citra (Manager) memecah task, Ari (Developer) & Bima (QA) bergegas ke Tech Hub!`;

    // Move agents to work locations
    const ari = agents.find(a => a.userData.id === 'agent_dev_01');
    const citra = agents.find(a => a.userData.id === 'agent_manager_01');
    const bima = agents.find(a => a.userData.id === 'agent_reviewer_01');

    if (citra) {
        citra.userData.thoughtText = `Citra: Mengkoordinasikan '${goal.slice(0, 20)}...'`;
        citra.userData.targetPos.set(citra.userData.info.work[0], 0, citra.userData.info.work[1]);
        citra.userData.walkSpeed = 0.08;
    }
    if (ari) {
        ari.userData.thoughtText = `Ari: Mengimplementasikan '${goal.slice(0, 20)}...'`;
        ari.userData.targetPos.set(ari.userData.info.work[0], 0, ari.userData.info.work[1]);
        ari.userData.walkSpeed = 0.08;
    }
    if (bima) {
        bima.userData.thoughtText = `Bima: Menyiapkan pengujian acceptance QA...`;
        bima.userData.targetPos.set(bima.userData.info.work[0], 0, bima.userData.info.work[1]);
        bima.userData.walkSpeed = 0.08;
    }

    addTickerItem(`🎯 GOAL BARU: "${goal}" diterima kota!`);

    // Pan camera to Tech Hub
    camera.position.set(-16, 22, 28);
    controls.target.set(-24, 6, 0);

    try {
        const result = await apiCall("submit_goal", goal);

        banner.style.display = 'none';

        if (ari) ari.userData.walkSpeed = 0.04;
        if (citra) citra.userData.walkSpeed = 0.04;
        if (bima) bima.userData.walkSpeed = 0.04;

        if (result && result.status === 'success') {
            if (ari) ari.userData.thoughtText = `Ari: Selesai membuat ${result.artifact_path}!`;
            if (bima) bima.userData.thoughtText = `Bima: Peer review disetujui (100%)!`;

            addTickerItem(`✅ ${result.artifact_path} tervalidasi & disetujui!`);

            // Handle Physical Building Construction & Citizen Recruitment
            const buildingBox = document.getElementById('res-building-banner');
            if (result.new_building) {
                const nb = result.new_building;
                const pos = nb.position;
                createStylizedHouse(pos.x, pos.z, 0x10b981);
                addTickerItem(`🏗️ Gedung baru selesai dibangun di (${pos.x}, ${pos.z})!`);

                if (nb.new_agent) {
                    spawnAgentToWorld(nb.new_agent);
                    addTickerItem(`👥 Warga baru ${nb.new_agent.name} (${nb.new_agent.role}) resmi bergabung!`);
                    document.getElementById('stat-pop').innerText = `${agents.length} Agents`;

                    buildingBox.style.display = 'block';
                    document.getElementById('res-building-text').innerText = 
                        `Gedung baru berhasil didirikan & ${nb.new_agent.name} (${nb.new_agent.role}) resmi menempati rumah barunya!`;
                }

                // Fly camera smoothly to the newly constructed building
                camera.position.set(pos.x + 12, 16, pos.z + 16);
                controls.target.set(pos.x, 3, pos.z);
            } else {
                buildingBox.style.display = 'none';
            }

            // Fill & Open Result Modal
            document.getElementById('res-goal').innerText = result.goal;
            document.getElementById('res-file').innerText = result.artifact_path;
            document.getElementById('res-review').innerText = `${(result.review_status || 'approved').toUpperCase()} (Skor: ${Math.round((result.review_score || 0.95) * 100)}%)`;
            document.getElementById('res-stdout').innerText = result.stdout || '(tidak ada output terminal)';
            document.getElementById('res-code').innerText = result.code || `# Kode disimpan di:\n# C:/AI_CITY/backend/workspace/${result.artifact_path}`;

            // Stderr section
            const stderrSection = document.getElementById('res-stderr-section');
            if (result.stderr && result.stderr.trim()) {
                stderrSection.style.display = 'block';
                document.getElementById('res-stderr').innerText = result.stderr;
            } else {
                stderrSection.style.display = 'none';
            }

            document.getElementById('result-modal').style.display = 'block';
        }
    } catch (err) {
        banner.style.display = 'none';
        console.error(err);
        alert('Terjadi kesalahan saat memproses goal: ' + err);
    }
}

// -----------------------------------------------------------------------------
// 12. LLM CONFIGURATION MODAL & API
// -----------------------------------------------------------------------------
async function openLlmModal() {
    const modal = document.getElementById('llm-modal');
    modal.style.display = 'block';
    document.getElementById('llm-alert').style.display = 'none';

    try {
        const status = await apiCall("get_llm_status");
        if (status) {
            document.getElementById('llm-provider-select').value = status.provider || 'mock';
            document.getElementById('llm-model-name').value = status.model || '';
            if (status.base_url) {
                document.getElementById('llm-base-url').value = status.base_url;
            }
            onLlmProviderChange();
        }
    } catch (e) {}
}

function closeLlmModal() {
    document.getElementById('llm-modal').style.display = 'none';
}

function onLlmProviderChange() {
    const sel = document.getElementById('llm-provider-select').value;
    const keyGroup = document.getElementById('group-api-key');
    const modelInput = document.getElementById('llm-model-name');
    const urlGroup = document.getElementById('group-base-url');

    if (sel === "groq") {
        keyGroup.style.display = 'block';
        urlGroup.style.display = 'none';
        modelInput.value = "llama-3.3-70b-versatile";
    } else if (sel === "openai") {
        keyGroup.style.display = 'block';
        urlGroup.style.display = 'none';
        modelInput.value = "gpt-4o-mini";
    } else if (sel === "ollama") {
        keyGroup.style.display = 'none';
        urlGroup.style.display = 'block';
        document.getElementById('llm-base-url').value = "http://127.0.0.1:11434";
        modelInput.value = "qwen2.5:3b";
    } else if (sel === "deepseek") {
        keyGroup.style.display = 'block';
        urlGroup.style.display = 'block';
        document.getElementById('llm-base-url').value = "https://api.deepseek.com/v1";
        modelInput.value = "deepseek-chat";
    } else {
        // Mock / Smart Offline
        keyGroup.style.display = 'none';
        urlGroup.style.display = 'none';
        modelInput.value = "smart-offline-engine";
    }
}

async function saveAndTestLlm() {
    const provider = document.getElementById('llm-provider-select').value;
    const apiKey = document.getElementById('llm-api-key').value;
    const model = document.getElementById('llm-model-name').value;
    const baseUrl = document.getElementById('llm-base-url').value;
    const alertBox = document.getElementById('llm-alert');
    const saveBtn = document.getElementById('btn-save-llm');

    saveBtn.innerText = "⏳ Menghubungkan...";
    saveBtn.disabled = true;

    try {
        const res = await apiCall("test_and_save_llm", provider, apiKey, model, baseUrl);
        alertBox.style.display = 'block';
        if (res && res.success) {
            alertBox.className = 'llm-test-alert alert-success';
            alertBox.innerText = `✅ ${res.message}`;
            updateLlmStatusDisplay(provider, model);
            setTimeout(closeLlmModal, 1500);
        } else {
            alertBox.className = 'llm-test-alert alert-error';
            alertBox.innerText = `❌ ${res ? res.message : 'Koneksi gagal'}`;
        }
    } catch (e) {
        alertBox.style.display = 'block';
        alertBox.className = 'llm-test-alert alert-error';
        alertBox.innerText = `❌ Terjadi kesalahan: ${e}`;
    } finally {
        saveBtn.innerText = "⚡ Test & Simpan";
        saveBtn.disabled = false;
    }
}

function updateLlmStatusDisplay(provider, model) {
    const pill = document.getElementById('stat-llm');
    const label = document.getElementById('llm-label');
    const icon = document.getElementById('llm-icon');

    if (provider === "groq") {
        label.innerText = `Groq (Llama-3.3-70b)`;
        icon.innerText = `⚡`;
        pill.className = `llm-pill`;
    } else if (provider === "openai") {
        label.innerText = `OpenAI (${model || 'GPT-4o'})`;
        icon.innerText = `🤖`;
        pill.className = `llm-pill`;
    } else if (provider === "ollama") {
        label.innerText = `Ollama (${model || 'Lokal'})`;
        icon.innerText = `🦙`;
        pill.className = `llm-pill`;
    } else {
        label.innerText = `Smart Engine (Offline)`;
        icon.innerText = `🧠`;
        pill.className = `llm-pill mock-mode`;
    }
}

// -----------------------------------------------------------------------------
// 13. CAMERA & CONTROLS
// -----------------------------------------------------------------------------
function setSimulationSpeed(spd, btn) {
    simulationSpeed = spd;
    document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
}

function setCameraPreset(view) {
    if (view === 'city') {
        camera.position.set(42, 34, 46);
        controls.target.set(0, 2, 0);
    } else if (view === 'plaza') {
        camera.position.set(0, 14, 24);
        controls.target.set(0, 2, 0);
    } else if (view === 'tech') {
        camera.position.set(-16, 18, 20);
        controls.target.set(-28, 8, 0);
    } else if (view === 'residential') {
        camera.position.set(0, 18, 42);
        controls.target.set(0, 4, 24);
    }
}

function onPointerClick(e) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(agents, true);

    if (intersects.length > 0) {
        let root = intersects[0].object;
        while (root.parent && root.parent !== scene) {
            root = root.parent;
        }
        selectAgent(root);
    }
}

function selectAgent(agent) {
    if (!agent || !agent.userData || !agent.userData.info) return;
    selectedAgent = agent;
    const data = agent.userData.info;

    document.getElementById('inspector-name').innerText = data.name;
    document.getElementById('inspector-role').innerText = data.role.replace('_', ' ').toUpperCase();
    document.getElementById('inspector-avatar').innerText = data.icon;
    document.getElementById('inspector-thought').innerText = agent.userData.thoughtText || `${data.name}: Menunggu instruksi…`;
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// -----------------------------------------------------------------------------
// 14. MISSING MODAL HELPERS (new UI)
// -----------------------------------------------------------------------------

function closeResultModal() {
    document.getElementById('result-modal').style.display = 'none';
}

function copyResultCode() {
    const code = document.getElementById('res-code').innerText;
    navigator.clipboard.writeText(code).then(() => {
        const btn = event.target.closest('button');
        if (btn) { btn.innerText = '✅ Tersalin!'; setTimeout(() => { btn.innerHTML = '📋 Salin Kode'; }, 1800); }
    }).catch(() => {
        alert('Copy gagal — pilih teks kode secara manual.');
    });
}

// Override openTaskModal / closeTaskModal to ensure both old and new HTML IDs work
function openTaskModal() {
    document.getElementById('task-modal').style.display = 'block';
}

function closeTaskModal() {
    document.getElementById('task-modal').style.display = 'none';
}

window.onload = init;
