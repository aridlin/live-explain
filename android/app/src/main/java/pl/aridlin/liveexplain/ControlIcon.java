package pl.aridlin.liveexplain;

import android.graphics.*;
import android.graphics.drawable.Drawable;

/** Small vector symbols, always accompanied by a readable text label. */
final class ControlIcon extends Drawable {
    private final Paint paint=new Paint(3);
    private final String kind;
    ControlIcon(String kind,int color,int size) {this.kind=kind;paint.setColor(color);paint.setStyle(Paint.Style.STROKE);paint.setStrokeWidth(1.8f);paint.setStrokeCap(Paint.Cap.ROUND);paint.setStrokeJoin(Paint.Join.ROUND);setBounds(0,0,size,size);}
    private void line(Canvas c,float... xy) {Path p=new Path();p.moveTo(xy[0],xy[1]);for(int i=2;i<xy.length;i+=2)p.lineTo(xy[i],xy[i+1]);c.drawPath(p,paint);}
    public void draw(Canvas c) {
        c.save();c.translate(getBounds().left,getBounds().top);c.scale(getBounds().width()/24f,getBounds().height()/24f);
        switch(kind) {
            case "play": line(c,8,5,19,12,8,19,8,5);break;
            case "pause":line(c,8,5,8,19);line(c,16,5,16,19);break;
            case "next":line(c,4,12,20,12,14,6);line(c,20,12,14,18);break;
            case "return":case "undo":line(c,9,5,3,10,9,15);line(c,3,10,15,10,19,14,19,20);break;
            case "replay":c.drawArc(4,4,20,20,-70,295,false,paint);line(c,4,4,4,10,10,10);break;
            case "branch":line(c,5,20,5,5,10,5);line(c,5,14,18,14,18,5);line(c,15,8,18,5,21,8);break;
            case "up":line(c,5,15,12,8,19,15);break;
            case "down":line(c,5,9,12,16,19,9);break;
            case "screen":c.drawRoundRect(3,4,21,17,2,2,paint);line(c,8,21,16,21);line(c,12,17,12,21);break;
            case "wifi":c.drawArc(2,4,22,24,220,100,false,paint);c.drawArc(6,9,18,21,220,100,false,paint);c.drawCircle(12,18,1,paint);break;
            case "check":line(c,4,12,10,18,20,6);break;
            case "skip":line(c,5,5,16,12,5,19,5,5);line(c,20,5,20,19);break;
            default:line(c,5,5,19,5);line(c,5,12,19,12);line(c,5,19,15,19);
        }
        c.restore();
    }
    public void setAlpha(int alpha){paint.setAlpha(alpha);invalidateSelf();}
    public void setColorFilter(ColorFilter f){paint.setColorFilter(f);invalidateSelf();}
    public int getOpacity(){return PixelFormat.TRANSLUCENT;}
}
