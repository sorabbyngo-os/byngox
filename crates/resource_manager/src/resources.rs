#[derive(Clone, Debug)]

pub struct SystemResources {

    pub ram_available_mb: u32,

    pub cpu_usage_percent: f32,

    pub gpu_usage_percent: f32,

    pub battery_percent: u8,

    pub temperature_celsius: f32,

}
