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
        this.sections = {};

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
        camera.position.set(9676.142752382411, -14331.26271822394, 8775.831370391728);
        
        
        const centerVector = new THREE.Vector3(0, 0, 0); 
        
        this.controls.target.set(9451.490341800703, -1271.9103938172098, 1787.7972245854658);

        container.appendChild(renderer.domElement);
        renderer.domElement.addEventListener('mousemove', this.onMouseMove, false);

        const animate = () => {

            requestAnimationFrame(animate);
            controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
            renderer.render(scene, camera);
            
            //  console.log(`Camera position: x=${camera.position.x}, y=${camera.position.y}, z=${camera.position.z}`);
            //console.log(`Controls target: x=${controls.target.x}, y=${controls.target.y}, z=${controls.target.z}`);


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
    
    scene_elements = async () => {
        try {
            await creator.create_nodes("http://127.0.0.1:8888/api/Nodes");
            await creator.create_lines("http://127.0.0.1:8888/api/Lines");
            await creator.create_surface("http://127.0.0.1:8888/api/Mesh");
            await creator.extrude_sections("http://127.0.0.1:8888/api/Lines",
                "http://127.0.0.1:8888/api/Section_assign",
                "http://127.0.0.1:8888/api/Sections")
            console.log("All tasks completed successfully");
        } catch (error) {
            console.error("An error occurred:", error);
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

    create_surface = async (path) => {  
        let parent = this;  
        const surface = await this.fetch_data(path);
        const elements = Object.values(surface);
        this.createMeshFilled(parent.nodes,elements);
    }

    extrude_sections = async (path_lines,path_assignations,path_cross_sections) => {
        const lines_dict = await this.fetch_data(path_lines);
        const section = await this.fetch_data(path_assignations);
        const cross_sections = await this.fetch_data(path_cross_sections);

        //console.log("cross_sections",cross_sections[0])
        //console.log("section",section)
        //console.log("lines_dict",lines_dict)
        Object.entries(lines_dict).forEach(([key, item]) => {
            const element_id = key
            const Nidi = item.nodei
            const Nidj = item.nodej

            const section_assigs = section[element_id]
            console.log(section_assigs)
            const sections_id = section_assigs.secid
            const rotation = section_assigs.rotation

            cross_sections.forEach((cross_section) => {
                if (cross_section.element_id == sections_id){
                    
                    const Polygon = cross_section.polygon;
                    const sec_type = cross_section.type;
                    this.extrude_line(Nidi,Nidj,rotation, Polygon,sec_type)
                }
            })



        });


    }
    

    addNode = (x, y, z) => {
       
        const geometry = new THREE.SphereGeometry(30, 30, 30);
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

    createMeshFilled = (nodes, elements) => {
        // Create materials
        const lineMaterial = new THREE.LineBasicMaterial({
            color: '#0C0C0C',  // Color for lines
            linewidth: 2,      // Set line width, note: may not be supported in all environments
            transparent: true, // Enable transparency
            opacity: 0.75,     // Set opacity to 75%
            depthTest: true,   // Enable depth testing
            depthWrite: false, // Optional: disable depth writing for a blending effect
            dashSize: 3,       // Define size of dashes
            gapSize: 1,        // Define size of gaps between dashes
        });
    
        const meshMaterial = new THREE.MeshPhongMaterial({
            color: '#00FFFF', // Cyan color for the mesh
            side: THREE.DoubleSide, // Render both sides of the material
            specular: 0x222222, // Controls the shine and highlights
            shininess: 35, // Adjust shininess for a glossy effect
            flatShading: true,
        });
    
        // Go through each element to draw the filled quads and the lines
        elements.forEach((element) => {
            const nodei = nodes[element.nodei];
            const nodej = nodes[element.nodej];
            const nodek = nodes[element.nodek];
            const nodel = nodes[element.nodel];
    
            // Create an array of vertices for the quad
            const vertices = [
                new THREE.Vector3(nodei.x, nodei.y, nodei.z),
                new THREE.Vector3(nodej.x, nodej.y, nodej.z),
                new THREE.Vector3(nodek.x, nodek.y, nodek.z),
                new THREE.Vector3(nodel.x, nodel.y, nodel.z)
            ];
    
            // Create the geometry for the quad
            const geometry = new THREE.BufferGeometry().setFromPoints(vertices);
            geometry.setIndex([0, 1, 2, 0, 2, 3]); // Define the two triangles forming the quad
            geometry.computeVertexNormals(); // Compute normals
    
            const mesh = new THREE.Mesh(geometry, meshMaterial);
    
            // Create lines for the edges of the quad
            const lineGeometry = new THREE.BufferGeometry().setFromPoints(vertices);
            lineGeometry.setIndex([0, 1, 1, 2, 2, 3, 3, 0]); // Define the lines using the vertices
            const line = new THREE.LineSegments(lineGeometry, lineMaterial);
    
            // Add the mesh and line to the scene
            this.scene.add(mesh);
            this.scene.add(line);
    
            // Uncomment the following line if you want the camera to look at the mesh
            // this.camera.lookAt(mesh.position);
        });
    }

        extrude_line = (Nidi,Nidj,rotation, Polygon,type) =>{
            let parent = this;
            let lines = parent.lines;
            const material = new THREE.LineBasicMaterial({ color: 0x0000ff });
            
            if (!(Nidi  in parent.nodes)  && !(Nidj  in parent.nodes)) {
                console.error('Invalid node index');
            }
    
            const sP = parent.nodes[Nidi];
            const eP = parent.nodes[Nidj];

            console.log("sP",sP)    
            const startPoint = new THREE.Vector3( sP.x, sP.y, sP.z )
        
            const endPoint = new THREE.Vector3( eP.x, eP.y, eP.z )
        
    
            const directionVector = endPoint.clone().sub(startPoint)
            const zDirenction = new THREE.Vector3(0,0,1)
            const path = new THREE.CatmullRomCurve3( [
                new THREE.Vector3(),
                directionVector.clone()
            ]);
    
            const position = startPoint
            const quaternion = new THREE.Quaternion()
                quaternion.setFromAxisAngle(
                    directionVector.normalize(),
                    0
                    )
    
            //console.log("inputs : **",path, cs_name, position, quaternion, directionVector, rotation)
    
            parent.createExrusion({ Polygon, position, quaternion, directionVector, rotation ,path,type})
            
    
        }


        createExrusion = async ({ Polygon, position, quaternion, directionVector, rotation ,path,type}) => {
            let firstPoint
            let lastPoint
            let shape = new THREE.Shape();

            
            Polygon.forEach((point, index, array) => {
                const rotCos = Math.cos(rotation);
                const rotSin = Math.sin(rotation);
            
                // Rotate the points according to the rotation angle
                const rotatedX = point.x * rotCos - point.y * rotSin;
                const rotatedY = point.x * rotSin + point.y * rotCos;
            
                if (index === 0) {
                    // Move to the first point after rotation
                    shape.moveTo(rotatedX, rotatedY);
                } else {
                    // Line to the subsequent points after rotation
                    shape.lineTo(rotatedX, rotatedY);
                }
            
                // Close the shape by connecting back to the first rotated point after the last point is reached
                if (index === array.length - 1) {
                    shape.closePath();
                }
            })
                
                const extrudeSettings = {
                    steps: 1,
                    // depth: 16,
                    extrudePath: path,
                    // bevelEnabled: true,
                    // bevelThickness: 1,
                    // bevelSize: 1,
                    // bevelOffset: 0,
                    // bevelSegments: 1
                };
    
                const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                const material = new THREE.MeshLambertMaterial({ color: this.getRandomRainbowColor() });
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy( position )
                mesh.rotateOnAxis( directionVector, rotation )
                /*
                const edges = new THREE.EdgesGeometry( geometry );
                const line = new THREE.LineSegments( edges, new THREE.LineBasicMaterial( { color: 0x838383 } ) );
                mesh.add( line );
                */
                

                if ( Polygon.length < 20 || !(type == "CHS") ){
                    const edges = new THREE.EdgesGeometry( geometry );
                    const line = new THREE.LineSegments( edges, new THREE.LineBasicMaterial( { color: 0xffffff } ) );
                    mesh.add( line );
                }
                    
    
                console.log("current scene",this.scene)
                console.log("mesh",mesh)
                this.cross_section.push(mesh)
                this.scene.add(mesh);
            };


            getRandomRainbowColor = () => {
                const colors = [
                    0xff0000, // Red
                    0xff7f00, // Orange
                    0xffff00, // Yellow
                    0x00ff00, // Green
                    0x0000ff, // Blue
                    0x4b0082, // Indigo
                    0x9400d3  // Violet
                ];
                return colors[Math.floor(Math.random() * colors.length)]
            }
    }
