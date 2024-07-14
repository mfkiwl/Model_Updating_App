class SCENE3D {
    constructor(MAIN_CONTAINER_ID) {
        this.MAIN_CONTAINER_ID = MAIN_CONTAINER_ID;
        this.nodes = {};
        this.conect = {};
        this.colored = 'random';
        this.width = '100%';
        this.lines = [];
        this.nodesArray = [];
        this.cross_section = [];
        this.mainContainer = document.getElementById(MAIN_CONTAINER_ID);
        this.mouse = new THREE.Vector2();
        this.raycaster = new THREE.Raycaster();
        this.intersected = null;
        this.onMouseMove = this.onMouseMove.bind(this);

    }

    create_scene = () => {
        this.container = document.createElement('div');
        const container = this.container;
        container.style.width = this.width;
        container.style.height = '500px';
        container.style.position = 'relative';

        this.mainContainer.appendChild(container);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        const renderer = this.renderer;

        this.scene = new THREE.Scene();
        const scene = this.scene;
        renderer.setPixelRatio(1.2);

        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.physicallyCorrectLights = false;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        renderer.outputEncoding = THREE.sRGBEncoding;

        scene.background = new THREE.Color("#D9D9D9");
   
// Ambient Light for even lighting
        const ambientLight = new THREE.AmbientLight(0xFFC528, 0.14);
        scene.add(ambientLight);
    
        // Point Lights for controlled intensity and direction
        
        const pointLight1 = new THREE.PointLight(0xE57505, 1);
        pointLight1.position.set(0, -5500, 0);
        scene.add(pointLight1);


        const pointLight2 = new THREE.PointLight(0xE57505, 1);
        pointLight1.position.set(0, 5500, 0);
        scene.add(pointLight1);
 /*
        const pointLight2 = new THREE.PointLight(0xFFFF00, 0.1);
        pointLight2.position.set(0, 1500, 5000);
        scene.add(pointLight2);

        const pointLight3 = new THREE.PointLight(0xFFFF00, 0.1);
        pointLight3.position.set(0, 0, -5000);
        scene.add(pointLight3);

        const pointLight4 = new THREE.PointLight(0xFFFF00, 0.1);
        pointLight4.position.set(0, 0, 5000);
        scene.add(pointLight4);
        */
        
        
        /*
        const lightA = new THREE.HemisphereLight(0xffffff, 0xffffff,2);
        scene.add(lightA);
        */

        let width = container.clientWidth;
        let height = container.clientHeight;

        this.camera = new THREE.PerspectiveCamera(
            75, // Field of view
            width / height, // Aspect ratio
            0.1, // Near clipping plane
            100000 // Far clipping plane
        );
        const camera = this.camera;
        this.controls = new THREE.OrbitControls(camera, renderer.domElement);
        const controls = this.controls;
        this.controls.enableDamping = false;
        //this.controls.dampingFactor = 0.9;

        camera.position.set(-1427.6862345705986, 825.7814372658702, 4715.351832717299); // Set camera position based on log values


        const centerVector = new THREE.Vector3(0, 0, 0); 

        this.controls.target.set(1014.6758159813975, -1919.3794991799784, 881.5088002285361); // Set controls target based on log values

        container.appendChild(renderer.domElement);
        renderer.domElement.addEventListener('mousemove', this.onMouseMove, false);

        const animate = () => {

            requestAnimationFrame(animate);
            controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
            renderer.render(scene, camera);
            //console.log(`Camera position: x=${camera.position.x}, y=${camera.position.y}, z=${camera.position.z}`);
            console.log(`Controls target: x=${controls.target.x}, y=${controls.target.y}, z=${controls.target.z}`);


        };
        animate();
    }



    /*
    onMouseMove = (event) => {
        event.preventDefault();

        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children);

        if (intersects.length > 0) {
            console.log(`Intersection at ${intersects[0].point.x}, ${intersects[0].point.y}, ${intersects[0].point.z}`);
        } else {
            const point = new THREE.Vector3();
            this.raycaster.ray.at(10, point); // 10 units from the camera
            console.log(`Ray at ${point.x}, ${point.y}, ${point.z}`);
        }
    }
    */

    onMouseMove = (event) => {
        event.preventDefault();
    
        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children);
    
        if (intersects.length > 0) {
            if (this.intersected !== intersects[0].object) {
                if (this.intersected) {
                    // Reset previous intersection object's material or color if needed
                }
    
                this.intersected = intersects[0].object;
    
                // Show tooltip
                if (this.intersected.name !== "CAT 793"){
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'block';
                tooltip.style.left = `${event.clientX}px`;
                tooltip.style.top = `${event.clientY}px`;
                tooltip.textContent = this.intersected.name;
                } // Assuming the name of the sphere is set to something meaningful
            }
        } else {
            if (this.intersected) {
                // Reset intersection object's material or color if needed
                this.intersected = null;
    
                // Hide tooltip
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'none';
            }
        }
    }

    render = () => {
        this.renderer.render(this.scene, this.camera);
    }

    fetch_data = async (path) => {

        try {
            const response = await fetch(path);
            const data = await response.json();
            return data;
        }
        catch(error) {
            console.error(error);
        }
    }
    

    create_nodes = async (path) => {
        const nodes_dict = await this.fetch_data(path);
        this.nodes = nodes_dict
        Object.values(nodes_dict).forEach((item) => {
            this.addNode(item.x, item.y, item.z);
        });
    }


    create_lines = async (path) => {
        const lines_dict = await this.fetch_data(path);
        Object.values(lines_dict).forEach((item) => {
            this.addLine(item.nodei, item.nodej);
        });
    }

    addNode = (x, y, z) => {
       
        const geometry = new THREE.SphereGeometry(100, 100, 100);
        const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        const node = new THREE.Mesh(geometry, material);

        node.position.set(x, y, z);

        this.scene.add(node);
    }

    addLine = (Nidi, Nidj) => {
        let parent = this;
        let lines = parent.lines;
        const material = new THREE.LineBasicMaterial({ color: 0x0000ff });
        
        if (!(Nidi  in parent.nodes)  && !(Nidj  in parent.nodes)) {
            console.error('Invalid node index');
        }

        const sP = parent.nodes[Nidi];
        const eP = parent.nodes[Nidj];
    
        const edge = [
            new THREE.Vector3(sP.x, sP.y, sP.z),
            new THREE.Vector3(eP.x, eP.y, eP.z)
        ];
    
        const geometry = new THREE.BufferGeometry().setFromPoints(edge);
        const line = new THREE.Line(geometry, material);
        this.scene.add(line);
    }



}