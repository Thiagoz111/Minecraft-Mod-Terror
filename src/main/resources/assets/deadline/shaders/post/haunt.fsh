#version 330

uniform sampler2D InSampler;

in vec2 texCoord;

layout(std140) uniform SamplerInfo {
    vec2 OutSize;
    vec2 InSize;
};

layout(std140) uniform HauntConfig {
    float Aberration;
    float Desaturate;
    float Vignette;
    float Warp;
    vec3 Tint;
};

out vec4 fragColor;

// DEAD LINE camera look: barrel warp, chromatic fringing, desaturation, tint, scanlines and a heavy vignette.
void main() {
    vec2 c = texCoord - 0.5;
    float r2 = dot(c, c);
    vec2 uv = 0.5 + c * (1.0 + Warp * r2);
    vec2 dir = (length(c) > 1e-4 ? normalize(c) : vec2(0.0)) * (Aberration / InSize) * (0.35 + r2 * 3.0);
    vec3 col = vec3(texture(InSampler, uv + dir).r, texture(InSampler, uv).g, texture(InSampler, uv - dir).b);
    float luma = dot(col, vec3(0.299, 0.587, 0.114));
    col = mix(col, vec3(luma), Desaturate) * Tint;
    col *= 0.93 + 0.07 * sin(uv.y * InSize.y * 3.14159);
    float v = smoothstep(0.95, 0.25, length(c) * 1.25);
    col *= mix(1.0, v, Vignette);
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        col = vec3(0.0);
    }
    fragColor = vec4(col, 1.0);
}
